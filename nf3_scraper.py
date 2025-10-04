import pandas as pd

TEAM_MAP = {
    '巨人': {'leg': 0, 'tm': 'G'},
    '中日': {'leg': 0, 'tm': 'D'},
    '阪神': {'leg': 0, 'tm': 'T'},
    '広島': {'leg': 0, 'tm': 'C'},
    'DeNA': {'leg': 0, 'tm': 'DB'},
    'ヤクルト': {'leg': 0, 'tm': 'S'},
    '日本ハム': {'leg': 1, 'tm': 'F'},
    '西武': {'leg': 1, 'tm': 'L'},
    'ロッテ': {'leg': 1, 'tm': 'M'},
    '楽天': {'leg': 1, 'tm': 'E'},
    'ソフトバンク': {'leg': 1, 'tm': 'H'},
    'オリックス': {'leg': 1, 'tm': 'Bs'},
}

def make_url(year, team_name, is_pitcher=False):
    team_info = TEAM_MAP[team_name]
    leg = team_info['leg']
    tm = team_info['tm']
    fp = 1 if is_pitcher else 0
    return f"https://nf3.sakura.ne.jp/php/stat_disp/stat_disp.php?y={year}&leg={leg}&tm={tm}&fp={fp}&dn=1&dk=0"

def fetch_nf3_data(url, is_pitcher=False):
    df = pd.read_html(url, header=0)[0]
    print("📌 列名一覧：", df.columns.tolist())

    df.columns = df.columns.str.replace(r'\s+', '', regex=True)

    if not is_pitcher:
        # ✅ ここからコピペで上書き！
        df = df.rename(columns={
            '打率': 'AVG', '出塁率': 'OBP', '長打率': 'SLG',
            '四球': 'BB', '三振': 'SO', '打席': 'PA'
        })

        cols_to_float = ['AVG', 'OBP', 'SLG', 'BB', 'SO', 'PA']
        for col in cols_to_float:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print("✅ AVG型:", df['AVG'].dtype)
        print("✅ SLG型:", df['SLG'].dtype)

        df['OPS'] = df['OBP'] + df['SLG']
        df['ISO'] = df['SLG'] - df['AVG']
        df['BB%'] = (df['BB'] / df['PA']).round(3)
        df['K%'] = (df['SO'] / df['PA']).round(3)

    else:
        df = df.rename(columns={
            '投球回': 'IP', '奪三振': 'SO', '与四球': 'BB', '被安打': 'H'
        })

        cols_to_float = ['IP', 'SO', 'BB', 'H']
        for col in cols_to_float:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if all(col in df.columns for col in ['IP', 'BB', 'H', 'SO']):
            df['WHIP'] = (df['BB'] + df['H']) / df['IP']
            df['奪三振率'] = df['SO'] / df['IP']
            df[['WHIP', '奪三振率']] = df[['WHIP', '奪三振率']].round(3)
        else:
            df['WHIP'] = None
            df['奪三振率'] = None

    
    return df
