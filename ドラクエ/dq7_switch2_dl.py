import os
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def download_game8_images(url, save_folder="game8_webp"):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"ページにアクセス中: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Game8は画像が多いので、ゆっくりスクロールして読み込ませる
            print("画像をスキャン中...")
            for _ in range(15):
                page.mouse.wheel(0, 1000)
                page.wait_for_timeout(300)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"読み込みエラー: {e}")
            return
        finally:
            browser.close()

    image_urls = set()
    
    # imgタグのあらゆる属性からWebPを探す
    for img in soup.find_all("img"):
        # Game8などのサイトで使われがちな属性を網羅
        attrs = ["src", "data-src", "data-original", "data-lazy-src", "srcset"]
        for attr in attrs:
            val = img.get(attr)
            if not val:
                continue
            
            # srcsetの場合は最初のURLを取得
            first_url = str(val).split(',')[0].split(' ')[0].strip()
            
            # URLの中に .webp が含まれているか、または画像っぽい拡張子をチェック
            low_url = first_url.lower()
            if ".webp" in low_url or ".png" in low_url or ".jpg" in low_url:
                full_url = urljoin(url, first_url)
                image_urls.add(full_url)

    print(f"発見された画像: {len(image_urls)} 件")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url
    }

    for i, img_url in enumerate(sorted(image_urls)):
        try:
            # クエリパラメータを除去して拡張子を確認
            clean_url = img_url.split('?')[0]
            
            # 保存する際、WebPとして扱う
            ext = ".webp" if ".webp" in img_url.lower() else os.path.splitext(clean_url)[1]
            if not ext:
                ext = ".webp"
                
            file_name = f"game8_{i:03d}{ext}"
            save_path = os.path.join(save_folder, file_name)
            
            res = requests.get(img_url, headers=headers, stream=True, timeout=10)
            if res.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in res.iter_content(1024):
                        f.write(chunk)
                print(f"保存: {file_name}")
        except Exception as e:
            pass

if __name__ == "__main__":
    target = "https://game8.jp/dq7/57652"
    download_game8_images(target)