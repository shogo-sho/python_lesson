import shutil
import unicodedata
from pathlib import Path

# ===== 設定 =====
source_dir = Path("/Users/shogo/Downloads")      
target_root = Path("/Users/shogo/PDF/取扱説明書")   
DRY_RUN = False  # Trueでプレビューのみ。OKならFalseに
# =========================================

CANONICAL = {"パナソニック", "東芝", "日立", "ソニー", "シャープ"}

EN_TO_JA = {
    "panasonic": "パナソニック",
    "national":  "パナソニック",
    "toshiba":   "東芝",
    "hitachi":   "日立",
    "sony":      "ソニー",
    "sharp":     "シャープ",
}

JA_VARIANTS = {
    "ﾊﾟﾅｿﾆｯｸ": "パナソニック",
    "ｿﾆｰ": "ソニー",
    "ｓｈａｒｐ": "シャープ",
    "ソニ－": "ソニー",
}

def nfkc_lower(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower()

def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s)

def canonicalize_maker(maker_raw: str) -> str | None:
    norm_lower = nfkc_lower(maker_raw)
    if norm_lower in EN_TO_JA:
        return EN_TO_JA[norm_lower]
    norm_ja = nfkc(maker_raw)
    if norm_ja in JA_VARIANTS:
        return JA_VARIANTS[norm_ja]
    if norm_ja in CANONICAL:
        return norm_ja
    return None

def ensure_unique(dst: Path) -> Path:
    if not dst.exists():
        return dst
    i = 2
    while True:
        cand = dst.with_name(f"{dst.stem}_{i}{dst.suffix}")
        if not cand.exists():
            return cand
        i += 1

def uppercase_letters_only(s: str) -> str:
    """数字はそのまま、アルファベットだけ大文字化"""
    return "".join(ch.upper() if ch.isalpha() else ch for ch in s)

def main():
    pdfs = [p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdfs:
        print("PDFが見つかりません。")
        return

    skipped = []
    for p in pdfs:
        stem_nfkc = nfkc(p.stem)
        if "_" not in stem_nfkc:
            skipped.append((p.name, "「メーカー_型番.pdf」形式ではない"))
            continue

        maker_raw, model_raw = stem_nfkc.split("_", 1)
        maker = canonicalize_maker(maker_raw.strip())
        model = uppercase_letters_only(model_raw.strip())

        if maker is None:
            skipped.append((p.name, f"メーカー名を認識できない: {maker_raw}"))
            continue

        brand_dir = target_root / maker
        brand_dir.mkdir(parents=True, exist_ok=True)

        dst = ensure_unique(brand_dir / f"{maker}_{model}.pdf")

        if DRY_RUN:
            print(f"[DRY] {p.name} → {dst}")
        else:
            shutil.move(str(p), str(dst))
            print(f"移動: {p.name} → {dst}")

    if skipped:
        print("\n--- 処理できなかったファイル ---")
        for name, reason in skipped:
            print(f"- {name} : {reason}")

if __name__ == "__main__":
    print(f"DRY_RUN = {DRY_RUN}")
    main()