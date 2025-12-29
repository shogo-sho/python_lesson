import os
import sys
from PIL import Image, ImageDraw, ImageFont

# --- 1. ファイルパスと設定 ---
WORK_DIR = "/Users/shogo/Documents/python_lesson/年賀状/"
OUTPUT_FILE = os.path.join(WORK_DIR, "nengajo_2026_pillow_final_v6.png") # ファイル名をv6に変更

# 画像ファイルのパス
RAPIDASH_PATH = os.path.join(WORK_DIR, "78.png")  # ギャロップ
PONYTA_PATH = os.path.join(WORK_DIR, "77.png")    # ポニータ
KADOMATSU_PATH = os.path.join(WORK_DIR, "images.png") # 門松
PLUM_RED_PATH = os.path.join(WORK_DIR, "梅の花(赤).png")
PLUM_WHITE_PATH = os.path.join(WORK_DIR, "梅の花(白).png")

# キャンバス設定
CANVAS_SIZE = (1000, 1480)
BG_COLOR_TOP = (255, 175, 189)
BG_COLOR_BTM = (255, 195, 160)

# --- 2. キャンバスと背景作成 ---
print("キャンバスを作成中...")
base_img = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 255))
draw = ImageDraw.Draw(base_img)

# グラデーション
for y in range(CANVAS_SIZE[1]):
    r = int(BG_COLOR_TOP[0] + (BG_COLOR_BTM[0] - BG_COLOR_TOP[0]) * y / CANVAS_SIZE[1])
    g = int(BG_COLOR_TOP[1] + (BG_COLOR_BTM[1] - BG_COLOR_TOP[1]) * y / CANVAS_SIZE[1])
    b = int(BG_COLOR_TOP[2] + (BG_COLOR_BTM[2] - BG_COLOR_TOP[2]) * y / CANVAS_SIZE[1])
    draw.line([(0, y), (CANVAS_SIZE[0], y)], fill=(r, g, b))

# --- 3. 背景装飾 ---
# 日の丸（月）
draw.ellipse((600, 100, 900, 400), fill=(217, 51, 63, 180))
draw.ellipse((550, 150, 750, 350), fill=(255, 255, 255, 100))

# 画像読み込み関数
def load_image(path):
    if os.path.exists(path):
        try:
            img = Image.open(path).convert("RGBA")
            return img
        except:
            return None
    return None

plum_red_img = load_image(PLUM_RED_PATH)
plum_white_img = load_image(PLUM_WHITE_PATH)

# 配置関数
def paste_image(target_img, x, y, size):
    if target_img:
        ratio = size / target_img.width
        h = int(target_img.height * ratio)
        img_resized = target_img.resize((size, h), Image.Resampling.LANCZOS)
        paste_x = int(x - size / 2)
        paste_y = int(y - h / 2)
        base_img.paste(img_resized, (paste_x, paste_y), img_resized)

# 梅の花の配置
# 左上エリア
paste_image(plum_red_img, 100, 100, size=180)
paste_image(plum_white_img, 220, 70, size=130)
paste_image(plum_red_img, 70, 220, size=100)
# 右上エリア
paste_image(plum_white_img, 900, 100, size=180)
paste_image(plum_red_img, 820, 60, size=130)
# 左サイド
paste_image(plum_white_img, 50, 600, size=140)
paste_image(plum_red_img, 130, 520, size=100)
# 右サイド
paste_image(plum_red_img, 950, 600, size=140)
paste_image(plum_white_img, 870, 520, size=100)


# --- 4. 門松の配置 ---
kadomatsu_img = load_image(KADOMATSU_PATH)
if kadomatsu_img:
    datas = kadomatsu_img.getdata()
    new_data = [(255, 255, 255, 0) if item[0]>230 and item[1]>230 and item[2]>230 else item for item in datas]
    kadomatsu_img.putdata(new_data)
    k_width = 320
    k_ratio = k_width / kadomatsu_img.width
    k_height = int(kadomatsu_img.height * k_ratio)
    kadomatsu_img = kadomatsu_img.resize((k_width, k_height), Image.Resampling.LANCZOS)
    base_img.paste(kadomatsu_img, (30, 820), kadomatsu_img)
    base_img.paste(kadomatsu_img, (650, 820), kadomatsu_img)
    print("門松を配置しました")


# --- 5. ポケモンの配置 ---
def paste_pokemon(path, x, y, size):
    img = load_image(path)
    if img:
        ratio = size / img.width
        h = int(img.height * ratio)
        img = img.resize((size, h), Image.Resampling.LANCZOS)
        final_x = int(x - size / 2)
        final_y = int(y)
        base_img.paste(img, (final_x, final_y), img)

paste_pokemon(RAPIDASH_PATH, 500, 300, 750)
paste_pokemon(PONYTA_PATH, 600, 650, 480)


# --- 6. 文字 ---
print("文字を描画中...")
# 白い帯（Y座標: 1150〜1400 → 中心Y: 1275）
draw.rounded_rectangle((150, 1150, 850, 1400), radius=20, fill=(255, 255, 255, 220))

try:
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font_hny = ImageFont.truetype(font_path, 80)
    font_year = ImageFont.truetype(font_path, 70)
except:
    font_hny = ImageFont.load_default()
    font_year = ImageFont.load_default()

# ▼▼▼ 修正点: Y座標を調整して垂直方向の中央に配置 ▼▼▼
# 枠の中心Y=1275を基準に、上下に振り分けます
draw.text((500, 1225), "Happy New Year", font=font_hny, fill=(212, 175, 55), anchor="mm")
draw.text((500, 1325), "2026", font=font_year, fill=(51, 51, 51), anchor="mm")

# --- 保存 ---
base_img.save(OUTPUT_FILE)
print(f"\n✅ 完了！テキストを白い枠の中央に配置しました:\n{OUTPUT_FILE}")