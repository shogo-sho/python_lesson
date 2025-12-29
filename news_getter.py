import requests
from bs4 import BeautifulSoup
import smtplib # メール送信の標準ライブラリ
from email.mime.text import MIMEText # メールの内容を作成するライブラリ
from email.header import Header # 日本語タイトルを使うためのライブラリ

# --- 1. 設定項目（ここを自分の情報に書き換えて！） ---
# ⚠️ここに通常のパスワードではなく、さっき発行した16桁のアプリパスワードを入れる
GMAIL_APP_PASSWORD = 'zlrb aaxd ukrk ezvs' 

# 送信元と送信先のメールアドレスは同じでOK。
SENDER_EMAIL = 's.hayakawa1995@gmail.com' # 例: 'shouchan@gmail.com'
RECEIVER_EMAIL = 's.hayakawa1995@gmail.com' # 例: 'shouchan@gmail.com'
# --------------------------------------------------

# 2. ニュース収集部分（変更なし）
url = "https://news.yahoo.co.jp/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
topics = soup.find_all("a", href=lambda href: href and "pickup" in href)

# 3. メール本文の作成
# メッセージは普通のテキストファイル形式で作成する
message_body = "\n"
message_body += "==============================\n"
message_body += "【 今日の主要ニュース（速報）】\n"
message_body += "自動取得：\n"
message_body += "==============================\n"

# 見出しとURLを本文に追加
for topic in topics:
    message_body += f"■ {topic.text}\n"
    message_body += f"   URL: {topic.get('href')}\n"
    message_body += "-" * 30 + "\n"

# 4. メールメッセージの構成（MIMETextを使う）
# 日本語の件名を使うため、Headerライブラリも使う
msg = MIMEText(message_body, 'plain', 'utf-8')
msg['Subject'] = Header(f"【自動速報】今日の主要ニュース", 'utf-8')
msg['From'] = SENDER_EMAIL
msg['To'] = RECEIVER_EMAIL

# 5. メール送信実行
try:
    # GmailのSMTPサーバーに接続し、暗号化（TLS）を開始
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    # ログイン（アドレスとアプリパスワード）
    server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
    
    # メール送信！
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    
    print("\n--- メール送信結果 ---")
    print("通知の送信に成功しました！受信トレイを確認してください。")
    print("---------------------\n")

except Exception as e:
    print(f"\n--- メール送信エラー ---")
    print(f"送信に失敗しました。以下のエラーを確認してください：\n{e}")
    print("原因：アプリパスワードが正しくない、または二段階認証が有効になっていません。")
    print("---------------------\n")