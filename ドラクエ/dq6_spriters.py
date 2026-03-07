import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def download_dq6_sheets_with_selenium(url):
    # 保存先の設定（Macのデスクトップ）
    save_folder = os.path.expanduser("~/Desktop/dq6_spriters_final")
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Chromeのオプション設定（ボット対策を回避）
    chrome_options = Options()
    # chrome_options.add_argument('--headless') # 動作確認のため、最初は画面を表示させます
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # WebDriverの起動
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"ブラウザでページを開いています... {url}")
        driver.get(url)
        
        # 完全に読み込まれるまで少し待機（Cloudflare対策）
        time.sleep(10) 

        # 読み込まれたHTMLをBeautifulSoupに渡す
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # シートへのリンクを取得
        links = []
        for a in soup.find_all('a', href=True):
            if '/sheet/' in a['href']:
                full_link = urljoin(url, a['href'])
                if full_link not in links:
                    links.append(full_link)

        if not links:
            print("やはりシートが見つかりません。画面を確認してください。")
            return

        print(f"合計 {len(links)} 個のシートを発見しました。順次ダウンロードします。")

        # 以降は各ページから画像をダウンロード（ここはrequestsでいけることが多いです）
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        
        for i, detail_url in enumerate(links):
            driver.get(detail_url)
            time.sleep(3) # 各ページの読み込み待機
            
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            # 「Download this Sheet」ボタン（/download/XXXX）を探す
            download_btn = detail_soup.find('a', href=lambda x: x and '/download/' in x)
            
            if download_btn:
                img_download_url = urljoin(url, download_btn['href'])
                
                # 画像のバイナリを取得
                # ※ダウンロードリンクは直接requestsで叩くと弾かれることがあるのでdriver.getでURLへ飛ぶ方法もあります
                # 今回はより安全に、ログインセッションを模した方法で試みます
                img_res = requests.get(img_download_url, headers=headers)
                
                # タイトル取得
                title_tag = detail_soup.find('span', class_='title-text')
                title = title_tag.get_text(strip=True) if title_tag else f"sheet_{i}"
                safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
                
                with open(os.path.join(save_folder, f"{safe_title}.png"), 'wb') as f:
                    f.write(img_res.content)
                print(f"[{i+1}/{len(links)}] 保存完了: {safe_title}.png")
            else:
                print(f"[{i+1}] ダウンロードリンクが見つかりません")

    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://www.spriters-resource.com/snes/dragonquest6jpn/"
    download_dq6_sheets_with_selenium(target_url)