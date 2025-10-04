# compress_and_sort_manuals.py
# 概要:
# 1) OCR済PDFを Ghostscript で同じフォルダに上書き圧縮（/ebook 既定）
# 2) ファイル名「メーカー_型番.pdf」からメーカーを日本語統一・型番は英字だけ大文字化
# 3) target_root/メーカー/「メーカー_型番.pdf」に自動移動（既存は上書き）
# python compress_pdfs.py

import subprocess
from pathlib import Path
import shutil
import sys
import unicodedata

# ====== 設定 ======
#in_dir     = Path("/Users/shogo/PDF/python入門")   # 圧縮したいPDFがある場所
in_dir     = Path("/Users/shogo/Downloads") 
#target_root = Path("/Users/shogo/PDF/python入門")  # メーカー別フォルダの親
target_root = Path("/Users/shogo/PDF/取扱説明書")
quality    = "ebook"  # "ebook"（推奨:スマホ/タブレット）/ "printer"（高画質）
# ===================

# メーカー統一表記（日本語）
CANONICAL = {"パナソニック", "東芝", "日立", "ソニー", "シャープ","サーモス"}

# 英語や表記ゆらぎ → 日本語
EN_TO_JA = {
    "panasonic": "パナソニック",
    "national":  "パナソニック",  # 旧ブランド
    "toshiba":   "東芝",
    "hitachi":   "日立",
    "sony":      "ソニー",
    "sharp":     "シャープ",
    "thermos": "サーモス",
}
JA_VARIANTS = {
    "ﾊﾟﾅｿﾆｯｸ": "パナソニック",
    "ｿﾆｰ": "ソニー",
    "ｓｈａｒｐ": "シャープ",
    "ソニ－": "ソニー", 
     "ｻｰﾓｽ": "サーモス", # 長音ゆらぎ
}

def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s)

def nfkc_lower(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower()

def uppercase_letters_only(s: str) -> str:
    """数字はそのまま、アルファベットだけ大文字化"""
    return "".join(ch.upper() if ch.isalpha() else ch for ch in s)

def canonicalize_maker(maker_raw: str) -> str | None:
    lower = nfkc_lower(maker_raw)
    if lower in EN_TO_JA:
        return EN_TO_JA[lower]
    ja = nfkc(maker_raw)
    if ja in JA_VARIANTS:
        return JA_VARIANTS[ja]
    if ja in CANONICAL:
        return ja
    return None

def find_gs_executable():
    for name in ("gs", "gswin64c", "gswin32c"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None

def compress_in_place(gs: str, pdf_path: Path, preset: str = "/ebook"):
    """
    Ghostscriptで一時ファイルに出力→元ファイルを上書き置換
    """
    tmp_out = pdf_path.with_suffix(".tmp_gs.pdf")
    if tmp_out.exists():
        tmp_out.unlink()

    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        f"-dPDFSETTINGS={preset}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={str(tmp_out)}",
        str(pdf_path),
    ]
    subprocess.run(cmd, check=True)

    # 上書き（古いの削除→リネーム）
    pdf_path.unlink(missing_ok=True)
    tmp_out.rename(pdf_path)

def move_to_brand_folder(src_pdf: Path):
    """
    ファイル名「メーカー_型番.pdf」を正規化して
    target_root/メーカー/メーカー_型番.pdf へ移動（既存は上書き）
    """
    stem = nfkc(src_pdf.stem)
    if "_" not in stem:
        return False, f"形式不正（メーカー_型番 でない）: {src_pdf.name}"

    maker_raw, model_raw = stem.split("_", 1)
    maker = canonicalize_maker(maker_raw.strip())
    if maker is None:
        return False, f"メーカー不明: {maker_raw}"

    model = uppercase_letters_only(model_raw.strip())
    brand_dir = target_root / maker
    brand_dir.mkdir(parents=True, exist_ok=True)

    dst = brand_dir / f"{maker}_{model}.pdf"

    # 既存があれば上書き
    if dst.exists():
        dst.unlink()

    # すでに同じ場所/同じ名前ならスキップ
    if src_pdf.resolve() == dst.resolve():
        return True, "既に所定の場所にあります"

    shutil.move(str(src_pdf), str(dst))
    return True, f"{dst}"

def main():
    # 前提チェック
    if not in_dir.exists():
        print(f"入力フォルダが見つかりません: {in_dir}", file=sys.stderr)
        sys.exit(1)
    target_root.mkdir(parents=True, exist_ok=True)

    gs = find_gs_executable()
    if not gs:
        print("Ghostscript が見つかりません。macなら `brew install ghostscript` 等で導入してください。", file=sys.stderr)
        sys.exit(1)

    quality_map = {"screen": "/screen", "ebook": "/ebook", "printer": "/printer", "prepress": "/prepress"}
    preset = quality_map.get(quality.lower(), "/ebook")

    pdfs = list(in_dir.glob("*.pdf"))
    if not pdfs:
        print("入力フォルダにPDFがありません。")
        return

    for i, pdf in enumerate(pdfs, 1):
        try:
            # 1) 同じフォルダで良圧縮（上書き）
            compress_in_place(gs, pdf, preset)
            # 2) メーカー別に移動（英語→日本語・型番は英字大文字）
            ok, msg = move_to_brand_folder(pdf)
            status = "OK" if ok else "SKIP"
            print(f"[{i}/{len(pdfs)}] {status}: {pdf.name} -> {msg}")
        except subprocess.CalledProcessError as e:
            print(f"[{i}/{len(pdfs)}] 失敗（Ghostscript）: {pdf.name} ({e})", file=sys.stderr)
        except Exception as e:
            print(f"[{i}/{len(pdfs)}] 失敗: {pdf.name} ({e})", file=sys.stderr)

if __name__ == "__main__":
    main()