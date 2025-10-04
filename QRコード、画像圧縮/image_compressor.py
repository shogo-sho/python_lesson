import os
from PIL import Image, ImageOps

# --- HEICをPillowで開けるように登録 ---
HEIF_OK = False
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_OK = True
except Exception:
    # pillow-heif未導入でも他拡張子は動く。HEICに当たったらエラーにする。
    pass

# フォルダ設定
input_folder = '/Users/shogo/画像/引越し用/圧縮前'
output_folder = '/Users/shogo/画像/引越し用/圧縮後'

# 出力フォルダがなければ作成
os.makedirs(output_folder, exist_ok=True)

# 対応する画像拡張子
valid_exts = ['.jpg', '.jpeg', '.png', '.heic', '.webp', '.bmp']

def to_rgb_without_alpha(img: Image.Image) -> Image.Image:
    """アルファ付きは白背景でRGB化、その他は必要に応じてRGBへ"""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        # Aチャンネルが無いP対策で一度RGBA化
        if "A" not in img.getbands():
            img = img.convert("RGBA")
        bg.paste(img, mask=img.getchannel("A"))
        return bg
    if img.mode != "RGB":
        return img.convert("RGB")
    return img

def compress_image(file_path, output_path, max_size=800, quality=80):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".heic" and not HEIF_OK:
        raise RuntimeError(
            "HEICを処理するには 'pillow-heif' が必要です。"
            " 例: python3.12 -m pip install 'pillow-heif'"
        )

    with Image.open(file_path) as img:
        # EXIFの回転を画像に反映（iPhone写真対策）
        img = ImageOps.exif_transpose(img)

        # 透過除去＋RGB化
        img = to_rgb_without_alpha(img)

        # リサイズ（長辺max_size）
        width, height = img.size
        if max(width, height) > max_size:
            if width >= height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # JPEG形式で保存（圧縮を少し丁寧に）
        img.save(
            output_path,
            'JPEG',
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling=1  # 4:2:2
        )

# 処理開始
for filename in os.listdir(input_folder):
    name, ext = os.path.splitext(filename)
    if ext.lower() in valid_exts:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"{name}.jpg")

        try:
            compress_image(input_path, output_path)
            os.remove(input_path)  # 元画像を削除（※心配ならここはコメントアウトで）
            print(f"✅ 圧縮完了：{filename} → {output_path}")
        except Exception as e:
            print(f"❌ エラー：{filename} - {e}")