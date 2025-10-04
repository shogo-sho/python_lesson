import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from nf3_scraper import make_url, fetch_nf3_data, TEAM_MAP

st.set_page_config(page_title="NPB成績ビューア", layout="wide")
st.title("NPB 選手成績ビューア（by アスカ♥）")

# UI：年度・区分・チーム
year = st.selectbox("年度", list(range(2025, 2004, -1)))
mode = st.radio("区分", ['野手', '投手'])
team = st.selectbox("チーム", TEAM_MAP.keys())

# データ取得
is_pitcher = (mode == '投手')
url = make_url(year, team, is_pitcher)
df = fetch_nf3_data(url, is_pitcher)

## 🔍 選手名の列を柔軟に探す
for name_col in ['選手名', '名前', '氏名']:
    if name_col in df.columns:
        player_col = name_col
        break
else:
    player_col = df.columns[1]  # なければ2列目を使う（保険）

# 選手選択（すでにOK）
players = df[player_col]
player = st.selectbox("選手を選んでよね", players)

# 成績取得（これもOK）
selected_rows = df[df[player_col] == player]

if not selected_rows.empty:
    row = selected_rows.iloc[0]
    st.subheader(f"{year}年 {team}・{player} の成績")
    st.dataframe(row.to_frame().T)

    # 👇グラフのコードがあるならここに続けて書いてOK
else:
    st.error(f"選手「{player}」の成績データが見つかりませんでした。")



