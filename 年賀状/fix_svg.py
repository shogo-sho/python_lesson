import base64
import requests

# 1. 外部画像のURL
url_ponyta = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/shiny/77.png"
url_rapidash = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/shiny/78.png"

# 2. 画像をダウンロードしてBase64文字列に変換する関数
def get_base64_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 画像データをBase64エンコード
        b64_data = base64.b64encode(response.content).decode('utf-8')
        return f"data:image/png;base64,{b64_data}"
    return "" # 失敗時は空文字

print("画像をダウンロード中...")
b64_ponyta = get_base64_image(url_ponyta)
b64_rapidash = get_base64_image(url_rapidash)

# 3. 修正版SVGの作成
# 変更点A: グラデーションを style="..." ではなく stop-color="..." に変更（互換性アップ）
# 変更点B: hrefにURLではなくBase64データを埋め込み
svg_content = f'''<svg width="1000" height="1480" viewBox="0 0 100 148" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sunriseGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffafbd" stop-opacity="1" />
      <stop offset="100%" stop-color="#ffc3a0" stop-opacity="1" />
    </linearGradient>
  </defs>

  <rect width="100" height="148" fill="url(#sunriseGradient)" />

  <circle cx="80" cy="30" r="15" fill="#d9333f" opacity="0.5" />
  <circle cx="75" cy="35" r="10" fill="#ffffff" opacity="0.4" />
  
  <image href="{b64_rapidash}" 
         x="15" y="35" height="70" width="70" opacity="0.9" />

  <image href="{b64_ponyta}" 
         x="40" y="65" height="45" width="45" />

  <rect x="10" y="110" width="80" height="30" fill="white" opacity="0.6" rx="2" ry="2" />

  <text x="50" y="122" font-family="'Times New Roman', serif" font-size="7" text-anchor="middle" fill="#c0392b" letter-spacing="0.5" font-weight="bold">Happy New Year</text>
  
  <text x="50" y="132" font-family="sans-serif" font-size="6" text-anchor="middle" fill="#333" letter-spacing="2">2026</text>
  
  <path d="M10,10 C30,20 70,20 90,10" stroke="#d9333f" stroke-width="0.5" fill="none" />
</svg>
'''

# 4. ファイルに保存
filename = "fixed_target.svg"
with open(filename, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"完了！ '{filename}' を生成しました。これを変換ツールに通してください。")