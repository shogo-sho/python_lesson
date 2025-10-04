from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json

# ===== 設定ファイル（前回の入出力フォルダを記録）=====
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

# --- 画像フォルダをダイアログで選択（初期＝前回の入力フォルダ or Documents） ---
def ask_src_dir():
    import tkinter as tk
    from tkinter import filedialog
    st = load_settings()
    initial_dir = get_valid_dir(st.get("last_input_dir")) or (Path.home() / "Documents")

    root = tk.Tk()
    root.withdraw()
    src_dir = filedialog.askdirectory(
        title="画像フォルダを選択",
        initialdir=str(initial_dir)
    )
    root.update()
    root.destroy()
    return Path(src_dir) if src_dir else None

# --- 保存先PDFファイルをダイアログで選択（初期＝前回の保存先 or Documents） ---
def ask_output_pdf(default_name="output.pdf"):
    import tkinter as tk
    from tkinter import filedialog
    st = load_settings()
    initial_dir = get_valid_dir(st.get("last_output_dir")) or (Path.home() / "Documents")

    root = tk.Tk()
    root.withdraw()
    out_pdf = filedialog.asksaveasfilename(
        title="保存先PDFを選択",
        initialdir=str(initial_dir),
        initialfile=default_name,
        defaultextension=".pdf",
        filetypes=[("PDFファイル", "*.pdf")]
    )
    root.update()
    root.destroy()
    return Path(out_pdf) if out_pdf else None

# --- 自然順ソート ---
def natural_key(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.findall(r"\d+|\D+", s)]

def list_images(folder: Path):
    exts = {".png", ".jpg", ".jpeg"}
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]
    return sorted(files, key=lambda p: natural_key(p.name))

# --- A4に収める（白余白あり・縦） ---
def fit_to_a4(im: Image.Image, dpi=300) -> Image.Image:
    import math
    a4_w = int(math.floor(8.27 * dpi))   # 210mm
    a4_h = int(math.floor(11.69 * dpi))  # 297mm
    ratio = min(a4_w / im.width, a4_h / im.height)
    new_w = max(1, int(im.width * ratio))
    new_h = max(1, int(im.height * ratio))
    im_resized = im.resize((new_w, new_h), Image.LANCZOS)
    canvas_img = Image.new("RGB", (a4_w, a4_h), "white")
    off_x = (a4_w - new_w) // 2
    off_y = (a4_h - new_h) // 2
    canvas_img.paste(im_resized, (off_x, off_y))
    return canvas_img

def convert_images_to_single_pdf(image_folder: Path, output_pdf_path, dpi=300):
    output_pdf_path = Path(output_pdf_path)  # Path型に統一
    images = list_images(image_folder)
    if not images:
        print("対応する画像が見つかりません。")
        return

    from reportlab.lib.pagesizes import A4
    a4_pt = (595.27, 841.89)
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_pdf_path), pagesize=A4)
    ok, skipped = 0, []

    for img_path in images:
        try:
            with Image.open(img_path) as im:
                # 透過PNGやCMYKをPDFに適したRGBへ
                if im.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", im.size, "white")
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                elif im.mode in ("P", "CMYK"):
                    im = im.convert("RGB")

                page_img = fit_to_a4(im, dpi=dpi)
                c.setPageSize(a4_pt)
                c.drawImage(ImageReader(page_img), 0, 0,
                            width=a4_pt[0], height=a4_pt[1])
                c.showPage()
                ok += 1
        except Exception as e:
            skipped.append((img_path.name, str(e)))

    c.save()
    print(f"[完了] {ok} 枚をA4 PDFにしました → {output_pdf_path}")
    if skipped:
        print("[読み込み失敗]")
        for name, err in skipped:
            print(f" - {name}: {err}")

def reveal_in_finder(path: Path):
    import subprocess
    script = f'''
    tell application "Finder"
        reveal POSIX file "{path}"
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)

if __name__ == "__main__":
    # 1) 入力フォルダ（初期=前回の入力 or Documents）
    src_dir = ask_src_dir()
    if not src_dir:
        print("キャンセルされました。")
    else:
        # 2) 保存先PDF（初期=前回の保存先 or Documents、デフォルト名=フォルダ名.pdf）
        default_name = f"{src_dir.name}.pdf"
        out_pdf = ask_output_pdf(default_name=default_name)
        if not out_pdf:
            print("キャンセルされました。")
        else:
            # 3) 変換
            convert_images_to_single_pdf(src_dir, out_pdf, dpi=300)
            reveal_in_finder(out_pdf)

            # 4) 今回の入出力フォルダを記憶（次回の初期値に）
            st = load_settings()
            st["last_input_dir"] = str(src_dir)
            st["last_output_dir"] = str(out_pdf.parent)
            save_settings(st)