from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json

# ===== 設定ファイル（前回選択の保存先）=====
SETTINGS_PATH = Path.home() / ".img2pdf_settings.json"

def load_settings() -> dict:
    """設定JSONを読み込み（なければ空dict）。"""
    try:
        if SETTINGS_PATH.exists():
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def save_settings(data: dict) -> None:
    """設定JSONを書き込み（失敗しても無視）。"""
    try:
        SETTINGS_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass

def get_valid_dir(path_str: str | None) -> Path | None:
    """文字列パスが有効ディレクトリならPathを返す。無効ならNone。"""
    if not path_str:
        return None
    p = Path(path_str)
    return p if (p.exists() and p.is_dir()) else None

# --- 親フォルダをダイアログで選択（初期＝前回の親 or Documents） ---
def ask_parent_dir():
    import tkinter as tk
    from tkinter import filedialog
    st = load_settings()
    initial_dir = get_valid_dir(st.get("last_parent_dir")) or (Path.home() / "Documents")

    root = tk.Tk()
    root.withdraw()
    parent = filedialog.askdirectory(
        title="親フォルダを選択（直下のサブフォルダを処理）",
        initialdir=str(initial_dir)
    )
    root.update()
    root.destroy()
    return Path(parent) if parent else None

# --- 出力先フォルダをダイアログで選択（初期＝前回の保存先 or Documents） ---
def ask_output_dir():
    import tkinter as tk
    from tkinter import filedialog
    st = load_settings()
    initial_dir = get_valid_dir(st.get("last_output_dir")) or (Path.home() / "Documents")

    root = tk.Tk()
    root.withdraw()
    out_dir = filedialog.askdirectory(
        title="PDFの保存先フォルダを選択",
        initialdir=str(initial_dir)
    )
    root.update()
    root.destroy()
    return Path(out_dir) if out_dir else None

# --- 自然順ソート ---
def natural_key(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.findall(r"\d+|\D+", s)]

# --- 画像列挙 ---
EXTS = {".png", ".jpg", ".jpeg"}
def list_images(folder: Path):
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS]
    return sorted(files, key=lambda p: natural_key(p.name))

# --- A4化（白余白・縦） ---
def fit_to_a4(im: Image.Image, dpi=300) -> Image.Image:
    import math
    a4_w = int(math.floor(8.27 * dpi))   # 横幅（210mm）
    a4_h = int(math.floor(11.69 * dpi))  # 縦幅（297mm）
    ratio = min(a4_w / im.width, a4_h / im.height)
    new_w = max(1, int(im.width * ratio))
    new_h = max(1, int(im.height * ratio))
    im_resized = im.resize((new_w, new_h), Image.LANCZOS)
    canvas_img = Image.new("RGB", (a4_w, a4_h), "white")
    off_x = (a4_w - new_w) // 2
    off_y = (a4_h - new_h) // 2
    canvas_img.paste(im_resized, (off_x, off_y))
    return canvas_img

# --- 重複を避けるファイル名 ---
def unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    stem, suffix = base_path.stem, base_path.suffix
    i = 1
    while True:
        candidate = base_path.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
        i += 1

# --- 1フォルダを PDF に変換 ---
def convert_folder_to_pdf(src_dir: Path, out_pdf: Path, dpi=300) -> tuple[int, list]:
    from reportlab.lib.pagesizes import A4
    a4_pt = (595.27, 841.89)

    images = list_images(src_dir)
    if not images:
        return 0, []  # 画像なし

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_pdf), pagesize=A4)
    ok, skipped = 0, []

    for img_path in images:
        try:
            with Image.open(img_path) as im:
                if im.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", im.size, "white")
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                elif im.mode in ("P", "CMYK"):
                    im = im.convert("RGB")

                page_img = fit_to_a4(im, dpi=dpi)
                c.setPageSize(a4_pt)
                c.drawImage(ImageReader(page_img), 0, 0, width=a4_pt[0], height=a4_pt[1])
                c.showPage()
                ok += 1
        except Exception as e:
            skipped.append((img_path.name, str(e)))

    c.save()
    return ok, skipped

# --- Finderで保存先を開く ---
def reveal_in_finder(path: Path):
    import subprocess
    script = f'''
    tell application "Finder"
        reveal POSIX file "{path}"
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)

# --- メイン処理 ---
if __name__ == "__main__":
    parent = ask_parent_dir()   # 親フォルダ選択（前回記憶を初期表示）
    out_dir = ask_output_dir()  # 保存先フォルダ選択（前回記憶を初期表示）
    if not parent or not out_dir:
        print("キャンセルされました。")
    else:
        subfolders = [p for p in parent.iterdir() if p.is_dir()]
        if not subfolders:
            print("サブフォルダが見つかりません。親フォルダ直下に画像フォルダを作ってください。")
        else:
            print(f"=== {len(subfolders)} フォルダを処理します ===")
            for idx, folder in enumerate(sorted(subfolders, key=lambda p: natural_key(p.name)), start=1):
                out_pdf = unique_path(out_dir / f"{folder.name}.pdf")
                print(f"[{idx}/{len(subfolders)}] {folder.name} → {out_pdf.name}")
                ok, skipped = convert_folder_to_pdf(folder, out_pdf, dpi=300)
                if ok == 0:
                    print(f"  - 画像なし（スキップ）")
                else:
                    print(f"  - {ok} 枚をPDF化")
                    if skipped:
                        print("  - 読み込み失敗：")
                        for name, err in skipped:
                            print(f"    * {name}: {err}")

            reveal_in_finder(out_dir)
            print(f"\n[完了] 出力先を開きました → {out_dir}")

        # ★ 最後に今回の選択を記憶（次回の初期値用）
        st = load_settings()
        st["last_parent_dir"] = str(parent)
        st["last_output_dir"] = str(out_dir)
        save_settings(st)