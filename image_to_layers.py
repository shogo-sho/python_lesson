#!/usr/bin/env python3
"""
2D画像を球体断面モデルに基づいた複数レイヤーに変換するツール

使い方:
    python image_to_layers.py 画像.png
    python image_to_layers.py 画像.png -n 16 -s sphere --preview
    python image_to_layers.py 画像.png -n 20 -s lens -o my_layers
"""

import argparse
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def convert_to_layers(
    image_path: str,
    num_layers: int = 10,
    output_dir: str = "output_layers",
    shape: str = "sphere",
    seed: int = 42,
) -> list[np.ndarray]:
    """
    画像を複数レイヤーに分解する。

    shape:
        sphere … 球体断面（前後は小さく、中央は大きい）
        lens   … レンズ形（球体より平たい）
        egg    … 非対称の卵形（前が急で後ろがなだらか）
    """
    rng = np.random.default_rng(seed)

    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    pixels = np.array(img)  # (H, W, 4)

    # 正規化座標 [-1, 1]
    xs = (np.arange(w) - w / 2) / (w / 2)
    ys = (np.arange(h) - h / 2) / (h / 2)
    xg, yg = np.meshgrid(xs, ys)  # (H, W)
    r = np.sqrt(xg**2 + yg**2)   # 中心からの距離（0〜√2）

    # 形状ごとの z_max（各ピクセルが取れる z の最大値）
    if shape == "sphere":
        # 球体断面: 半径1の球をスライスしたイメージ
        z_max = np.sqrt(np.maximum(0.0, 1.0 - r**2))
    elif shape == "lens":
        # レンズ形: 球より薄い（2乗で急速に縮む）
        z_max = np.maximum(0.0, 1.0 - r**2)
    elif shape == "egg":
        # 卵形: 前半（z>0）は球体、後半（z<0）はレンズより薄い非対称形
        z_max = np.sqrt(np.maximum(0.0, 1.0 - r**2))
    else:
        z_max = np.sqrt(np.maximum(0.0, 1.0 - r**2))

    valid = z_max > 1e-6  # 有効ピクセル（円の内側）

    # 各ピクセルに z を割り当て: [-z_max, z_max] の一様乱数
    z_raw = rng.uniform(-1.0, 1.0, size=(h, w))

    if shape == "egg":
        # 卵形: 正の z 側（前方）は通常の球体、負の z 側（後方）は薄い
        z_assign = np.where(z_raw >= 0, z_raw * z_max, z_raw * z_max * 0.5)
        # 全体を [-1, 1] に再スケール
        effective_zmax = np.where(z_raw >= 0, z_max, z_max * 0.5)
        z_assign = z_raw * effective_zmax
    else:
        z_assign = z_raw * z_max  # [-z_max, z_max]

    # z を [0, num_layers-1] のレイヤー番号にマッピング
    # z = -1 → layer 0（最前面）、z = +1 → layer N-1（最奥）
    layer_idx = ((z_assign + 1.0) / 2.0 * num_layers).astype(int)
    layer_idx = np.clip(layer_idx, 0, num_layers - 1)

    # レイヤー画像を生成
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    layer_arrays = []
    print(f"\n画像サイズ: {w} x {h}  |  レイヤー数: {num_layers}  |  形状: {shape}")
    print("-" * 45)

    for i in range(num_layers):
        arr = np.zeros((h, w, 4), dtype=np.uint8)
        mask = valid & (layer_idx == i)
        arr[mask] = pixels[mask]
        layer_arrays.append(arr)

        img_out = Image.fromarray(arr)
        img_out.save(out_path / f"layer_{i:03d}.png")

        bar_len = mask.sum() * 30 // (valid.sum() or 1)
        print(f"  Layer {i:3d}: {'█' * bar_len:<30} {mask.sum():6d} px")

    print(f"\n✓ {num_layers} レイヤーを '{out_path}/' に保存しました")
    return layer_arrays


def create_preview(layer_arrays: list[np.ndarray], output_dir: str) -> None:
    """全レイヤーを横に並べたプレビュー画像と、横から見た断面図を生成する。"""
    n = len(layer_arrays)
    if n == 0:
        return

    h, w = layer_arrays[0].shape[:2]
    out_path = Path(output_dir)

    # ── 1. 横並びプレビュー ────────────────────────────
    GAP = 4
    LABEL_H = 20
    total_w = n * w + (n - 1) * GAP
    total_h = h + LABEL_H
    preview = Image.new("RGBA", (total_w, total_h), (40, 40, 40, 255))
    draw = ImageDraw.Draw(preview)

    for i, arr in enumerate(layer_arrays):
        x = i * (w + GAP)
        preview.paste(Image.fromarray(arr), (x, LABEL_H))
        draw.text((x + w // 2 - 8, 2), f"{i}", fill=(200, 200, 200, 255))

    preview.save(out_path / "preview_layers.png")
    print(f"✓ レイヤープレビュー → {out_path}/preview_layers.png")

    # ── 2. 横から見た断面図（pixel count per layer） ────
    counts = [np.any(arr[:, :, 3] > 0, axis=1).sum() + arr[:, :, 3].sum() // 255
              for arr in layer_arrays]
    # より正確に: 各レイヤーの不透明ピクセル数
    counts = [(arr[:, :, 3] > 0).sum() for arr in layer_arrays]

    max_count = max(counts) or 1
    VIZ_H = 200
    VIZ_W = n * 20 + 40
    viz = Image.new("RGB", (VIZ_W, VIZ_H + 30), (30, 30, 30))
    vd = ImageDraw.Draw(viz)

    for i, cnt in enumerate(counts):
        bar_h = int(cnt / max_count * VIZ_H)
        x0 = 20 + i * 20
        x1 = x0 + 16
        y0 = VIZ_H - bar_h
        y1 = VIZ_H
        # 中央ほど明るい青、端ほど暗い
        ratio = 1 - abs(2 * i / (n - 1) - 1) if n > 1 else 1
        color = (int(40 + 180 * ratio), int(100 + 120 * ratio), int(200 + 50 * ratio))
        vd.rectangle([x0, y0, x1, y1], fill=color)

    vd.text((10, VIZ_H + 5), "← Front      Layers      Back →", fill=(180, 180, 180))
    viz.save(out_path / "preview_sideview.png")
    print(f"✓ 断面グラフ          → {out_path}/preview_sideview.png")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="2D画像を球体断面モデルの複数レイヤーに変換するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python image_to_layers.py icon.png
  python image_to_layers.py icon.png -n 16 --preview
  python image_to_layers.py icon.png -n 20 -s lens -o my_output --preview
        """,
    )
    parser.add_argument("image", help="入力画像のパス（PNG / JPG など）")
    parser.add_argument(
        "-n", "--num-layers", type=int, default=10,
        help="レイヤー数（デフォルト: 10）",
    )
    parser.add_argument(
        "-o", "--output", default="output_layers",
        help="出力ディレクトリ（デフォルト: output_layers）",
    )
    parser.add_argument(
        "-s", "--shape",
        choices=["sphere", "lens", "egg"],
        default="sphere",
        help="断面の形状: sphere=球体 / lens=レンズ形 / egg=卵形（デフォルト: sphere）",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="乱数シード（再現性用、デフォルト: 42）",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="プレビュー画像と断面グラフを生成する",
    )

    args = parser.parse_args()
    layers = convert_to_layers(
        image_path=args.image,
        num_layers=args.num_layers,
        output_dir=args.output,
        shape=args.shape,
        seed=args.seed,
    )

    if args.preview:
        create_preview(layers, args.output)


if __name__ == "__main__":
    main()
