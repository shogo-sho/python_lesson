import pandas as pd
import requests
from bs4 import BeautifulSoup

# NPB 2024 成績ページ
URLS = {
    '打者_セ': 'https://npb.jp/bis/2024/stats/bat_c.html',
    '打者_パ': 'https://npb.jp/bis/2024/stats/bat_p.html',
    '投手_セ': 'https://npb.jp/bis/2024/stats/pit_c.html',
    '投手_パ': 'https://npb.jp/bis/2024/stats/pit_p.html',
}

def fetch_table(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table')
    df = pd.read_html(str(table), header=0)[0]  # 👈 header=0 を明示
    df.columns = df.columns.str.strip()  # 👈 空白除去
    print("✅ カラム一覧:", df.columns.tolist())  # ←これが重要！
    return df


def add_batter_metrics(df):
    df = df.copy()
    df.columns = df.columns.str.replace(r'\s+', '', regex=True)  # 改行・空白を全て除去
    df = df.rename(columns={
        '打率': 'AVG',
        '出塁率': 'OBP',
        '長打率': 'SLG',
        '四球': 'BB',
        '三振': 'SO',
        '打席': 'PA',
    })

    df['OPS'] = df['OBP'] + df['SLG']
    df['ISO'] = df['SLG'] - df['AVG']
    df['BB%'] = df['BB'] / df['PA']
    df['K%'] = df['SO'] / df['PA']
    df[['OPS', 'ISO', 'BB%', 'K%']] = df[['OPS', 'ISO', 'BB%', 'K%']].round(3)

    return df


def add_pitcher_metrics(df):
    df = df.copy()
    df['WHIP'] = (df['与四球'] + df['被安打']) / df['投球回']
    df['K-BB'] = df['奪三振'] - df['与四球']
    df['奪三振率'] = df['奪三振'] / df['投球回']
    df[['WHIP', 'K-BB', '奪三振率']] = df[['WHIP', 'K-BB', '奪三振率']].round(3)
    return df

def load_all_data():
    batters = pd.concat([
        add_batter_metrics(fetch_table(URLS['打者_セ'])),
        add_batter_metrics(fetch_table(URLS['打者_パ']))
    ])
    pitchers = pd.concat([
        add_pitcher_metrics(fetch_table(URLS['投手_セ'])),
        add_pitcher_metrics(fetch_table(URLS['投手_パ']))
    ])
    return batters, pitchers
