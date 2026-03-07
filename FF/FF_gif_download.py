import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO

def download_dq_images(url, save_folder="FF"):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        print(f"--- 接続成功: {url} ---")
    except Exception as e:
        print(f"ページの取得に失敗: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    
    # PNGとGIFの両方を収集
    img_urls = []
    for img in img_tags:
        src = img.get('src')
        if src:
            ext = src.lower()
            if ext.endswith('.png') or ext.endswith('.gif'):
                img_urls.append(urljoin(url, src))
    
    img_urls = list(set(img_urls))
    print(f"対象画像数: {len(img_urls)} 個")

    for i, img_url in enumerate(img_urls):
        try:
            res = requests.get(img_url, headers=headers, timeout=10)
            res.raise_for_status()
            
            # 画像を開く
            img = Image.open(BytesIO(res.content))
            
            # --- 透過処理の改善 ---
            if img.mode != 'RGB':
                # RGBAやPモード（パレット）をRGBAに統一
                img = img.convert("RGBA")
                # 白背景を作成
                background = Image.new("RGB", img.size, (255, 255, 255))
                # 合成（アルファチャンネルがある場合のみマスクを使用）
                background.paste(img, mask=img.split()[3])
                final_img = background
            else:
                final_img = img

            # ファイル名の決定
            base_name = os.path.basename(urlparse(img_url).path)
            file_name = os.path.splitext(base_name)[0] + ".png"
            save_path = os.path.join(save_folder, file_name)

            # 保存
            final_img.save(save_path, "PNG", quality=90)
            print(f"[{i+1}/{len(img_urls)}] 保存成功: {file_name}")

        except Exception as e:
            # ここで何が起きたか詳細を表示するようにしました
            print(f"[{i+1}] エラー発生 ({img_url}): {e}")

if __name__ == "__main__":
    target_url = "http://osyou2019.s1007.xrea.com/gba_ff4.html"
    download_dq_images(target_url)