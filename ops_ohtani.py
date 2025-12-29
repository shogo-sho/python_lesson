import pandas as pd
import numpy as np

# 全チームのコードリスト
TM_CODES = {
    'G': '読売', 'T': '阪神', 'DB': 'DeNA', 'C': '広島', 
    'YS': 'ヤクルト', 'D': '中日', 'H': 'SB', 'F': '日ハム', 
    'M': 'ロッテ', 'E': '楽天', 'B': 'オリックス', 'L': '西武'
}

# データを格納するためのリストを2つ用意
all_pitching_data = [] # fp=1
all_batting_data = []  # fp=0

print("--- ⚾️ 投打データの統合収集を開始 ---")

for code, team_name in TM_CODES.items():
    # 投手成績のURL (fp=1)
    url_pitching = f"https://nf3.sakura.ne.jp/php/stat_disp/stat_disp.php?y=0&leg=0&tm={code}&fp=1&dn=1&dk=0"
    # 打撃成績のURL (fp=0)
    url_batting = f"https://nf3.sakura.ne.jp/php/stat_disp/stat_disp.php?y=0&leg=0&tm={code}&fp=0&dn=1&dk=0"
    
    print(f"✅ 収集中: {team_name} ({code})...")
    
    try:
        # 投手データ取得
        df_list_p = pd.read_html(url_pitching, header=0)
        df_p = df_list_p[-1] 
        df_p = df_p[df_p['背番'] != '背番']
        df_p['Team'] = team_name
        df_p['DataType'] = 'P' # 投手であることを示すフラグ
        all_pitching_data.append(df_p)
        
        # 打者データ取得
        df_list_b = pd.read_html(url_batting, header=0)
        df_b = df_list_b[-1]
        df_b = df_b[df_b['背番'] != '背番']
        df_b['Team'] = team_name
        df_b['DataType'] = 'B' # 打者であることを示すフラグ
        all_batting_data.append(df_b)
        
    except Exception as e:
        print(f"❌ エラー発生: {team_name} のデータ取得に失敗しました ({e})")

print("--- 収集完了 ---")

# 2. マスターデータの作成
df_pitching_master = pd.concat(all_pitching_data, ignore_index=True)
df_batting_master = pd.concat(all_batting_data, ignore_index=True)

print("\n" + "=" * 50)
print(f"【 投手データ合計: {len(df_pitching_master)} 行 | 打者データ合計: {len(df_batting_master)} 行 】")
print("=" * 50)
print("投手マスター (先頭3行):\n", df_pitching_master[['名前', 'Team', '防御率', '回数', '三振']].head(3))
print("\n打者マスター (先頭3行):\n", df_batting_master[['名前', 'Team', '打率', '安打', '本塁']].head(3))

# 2. マスターデータの作成 (pd.concatの行はそのまま)
df_pitching_master = pd.concat(all_pitching_data, ignore_index=True)
df_batting_master = pd.concat(all_batting_data, ignore_index=True)

# ⭐️⭐️⭐️ 追加するコードはここ！ ⭐️⭐️⭐️
df_pitching_master = df_pitching_master[df_pitching_master['名前'] != '合計'].copy()
df_batting_master = df_batting_master[df_batting_master['名前'] != '合計'].copy()

# 3. 結果表示 (行数が減っていることを確認)
# ... (後のprint文に続く)

# ⭐️⭐️⭐️ 投打データの結合に挑戦 ⭐️⭐️⭐️

# 投手と打者の両方のデータが存在する選手を「名前」をキーに結合する
# how='outer' は、どちらかの表にしか存在しない選手（例：純粋な野手）も残すための指定よ
df_master_combined = pd.merge(
    df_pitching_master, 
    df_batting_master, 
    on='名前', 
    how='outer',
    suffixes=('_P', '_B') # 列名の衝突を防ぐため、サフィックスを付ける
)

print("\n\n" + "=" * 50)
print("【 ⭐️ 投打統合マスターデータ (最初の5行) ⭐️ 】")
print("=" * 50)
print(df_master_combined.head())

print(f"\n✅ 最終統合された行数: {len(df_master_combined)} (重複なしの全選手数)")