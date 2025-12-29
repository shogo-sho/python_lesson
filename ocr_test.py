import pytesseract
from PIL import Image
import sys

# コマンドライン引数チェック
if len(sys.argv) < 2:
    print("画像をドラッグ＆ドロップして実行してください")
    sys.exit(1)

image_path = sys.argv[1]

try:
    print(f"読み込み中: {image_path} ...")
    img = Image.open(image_path)
    
    # 【ここが重要】
    # --psm 6 : ブロックとしてテキストが並んでいると仮定して読む（表紙などに強い）
    # --psm 11 : 散らばったテキストとして読む（さらに強力）
    custom_config = r'--psm 6' 
    
    # lang='jpn+eng' で日本語と英語を同時に狙う
    text = pytesseract.image_to_string(img, lang='jpn+eng', config=custom_config)
    
    if text.strip() == "":
        print("⚠ 文字が見つかりませんでした。設定を変えて再試行します...")
        # 失敗したら PSM 11 (疎なテキストモード) で再チャレンジ
        text = pytesseract.image_to_string(img, lang='jpn+eng', config='--psm 11')

    print("\n" + "=" * 30)
    print("   📖 読み取り結果")
    print("=" * 30)
    print(text)
    print("=" * 30)

except Exception as e:
    print(f"❌ エラー: {e}")