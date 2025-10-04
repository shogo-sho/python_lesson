# -*- coding: utf-8 -*-
"""
入力: CSV(名前,URL)
出力: 個別PNG (QRは4cm四方, 下に名前を印字, ファイル名: 名前.png)

例のCSV:
名前,URL
収納A,https://photos.app.goo.gl/xxxxx
ラック1A,https://photos.app.goo.gl/yyyyy
"""

import csv
import os
import re
import unicodedata
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

# ===== 設定 =====
CSV_FILE = "/Users/shogo/Documents/python_lesson/QRコード、画像圧縮/引越しQRコード作成用.csv"
OUT_DIR = "/Users/shogo/画像/QRコード"
DPI = 300
QR_SIZE_CM = 4.0
SAFE_CHAR_RE = re.compile(r'[\\/:*?"<>|]')

def sanitize_filename(name: str) -> str:
    s = unicodedata.normalize("NFKC", name.strip())
    s = SAFE_CHAR_RE.sub("_", s)
    return s or "noname"

def make_qr(url: str, qr_px: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url.strip())
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((qr_px, qr_px), Image.LANCZOS)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    qr_px = int(QR_SIZE_CM / 2.54 * DPI)  # cm→inch→px

    with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            name, url = row[0].strip(), row[1].strip()
            if not name or not url:
                continue

            safe = sanitize_filename(name)
            qr_img = make_qr(url, qr_px)

            out_path = os.path.join(OUT_DIR, f"{safe}.png")
            qr_img.save(out_path, dpi=(DPI, DPI))
            print(f"✅ {name} → {out_path}")

if __name__ == "__main__":
    main()