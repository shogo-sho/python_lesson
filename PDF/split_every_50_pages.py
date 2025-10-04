# split_every_50_pages_with_history_and_delete.py
# 50ページごとに分割 → すべて成功したら元PDFを削除
# 初期フォルダは last_folder.json に保存した前回選択を使う

import json
from pathlib import Path
from tkinter import Tk, filedialog
from pypdf import PdfReader, PdfWriter

CHUNK = 50
HISTORY_FILE = Path("last_folder.json")  # スクリプトと同じ場所に作成
DELETE_ORIGINAL = True                   # 分割後に元ファイルを削除

def load_last_folder() -> str | None:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8")).get("last_folder")
        except Exception:
            return None
    return None

def save_last_folder(folder: str):
    HISTORY_FILE.write_text(json.dumps({"last_folder": folder}, ensure_ascii=False, indent=2), encoding="utf-8")

def choose_folder() -> Path:
    root = Tk(); root.withdraw()
    init_dir = load_last_folder() or "/"
    folder = filedialog.askdirectory(title="分割したいPDFフォルダを選んでください", initialdir=init_dir)
    root.destroy()
    if not folder:
        raise ValueError("フォルダが選択されませんでした")
    save_last_folder(folder)
    return Path(folder)

def split_pdf(pdf_path: Path, chunk: int = CHUNK):
    # 読み込み
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        print(f"読み込み失敗: {pdf_path.name} ({e})")
        return

    # 暗号化PDFはスキップ（必要ならパス対応を追加）
    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")  # 空パスワード試行
        except Exception:
            print(f"暗号化のためスキップ: {pdf_path.name}")
            return

    n = len(reader.pages)
    if n <= chunk:
        print(f"スキップ（{n}ページ ≤ {chunk}）: {pdf_path.name}")
        return

    stem = pdf_path.stem
    parent = pdf_path.parent
    created = []  # 生成に成功したファイルを記録

    # 分割生成
    try:
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            writer = PdfWriter()
            for i in range(start, end):
                writer.add_page(reader.pages[i])
            # メタデータの引き継ぎは任意
            try:
                if reader.metadata:
                    writer.add_metadata(reader.metadata)
            except Exception:
                pass
            out_path = parent / f"{stem}-{start+1}-{end}.pdf"
            with open(out_path, "wb") as f:
                writer.write(f)
            created.append(out_path)
            print(f"作成: {out_path.name}")
    except Exception as e:
        print(f"分割中に失敗: {pdf_path.name} ({e})")
        # 途中まで作ったファイルを削除（クリーンアップ）
        for p in created:
            try:
                p.unlink()
            except Exception:
                pass
        return

    # ここまで来たら全分割成功 → 原本を削除
    if DELETE_ORIGINAL:
        try:
            pdf_path.unlink()
            print(f"元ファイルを削除: {pdf_path.name}")
        except Exception as e:
            print(f"元ファイル削除に失敗: {pdf_path.name} ({e})")

def main():
    folder = choose_folder()
    pdfs = list(folder.glob("*.pdf"))
    if not pdfs:
        print("PDFが見つかりません。")
        return
    for pdf in pdfs:
        split_pdf(pdf, CHUNK)

if __name__ == "__main__":
    main()