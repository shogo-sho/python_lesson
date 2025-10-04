# -*- coding: utf-8 -*-
# Streamlit app: ポケモン種族値＋特性検索（固定CSV・ボタンなし・タブ表示）
# 起動したい時は、ターミナルに　streamlit run pokemon_stat_viewer_streamlit.py

import re
import unicodedata
import pandas as pd
import streamlit as st

# ------------------------------
# 設定
# ------------------------------
CSV_PATH = "/Users/shogo/Documents/csv/ポケモン全国図鑑一覧.csv"  # この .py と同じフォルダに置く

st.set_page_config(page_title="ポケモン 種族値・特性 検索", page_icon="🔎", layout="centered")

# ------------------------------
# ユーティリティ
# ------------------------------
def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.lower().strip()
    s = re.sub(r"[・･\u3000\s]+", "", s)
    return s

def collect_ability_columns(cols):
    candidates = ["特性", "特性1", "特性2", "夢特性", "隠れ特性", "ability", "ability1", "ability2", "hidden"]
    found = []
    for c in cols:
        nc = normalize_text(c)
        for cand in candidates:
            if normalize_text(cand) in nc:
                found.append(c)
                break
    # 重複除去（順序維持）
    return list(dict.fromkeys(found))

def extract_abilities(row, ability_cols):
    vals = []
    for c in ability_cols:
        v = row.get(c, "")
        if pd.isna(v) or v is None:
            continue
        s = str(v)
        parts = re.split(r"[\/／,、・　\|\s]+", s)
        for p in parts:
            p = p.strip()
            if p and p != "-":
                vals.append(p)
    # 重複除去（順序維持）
    out, seen = [], set()
    for v in vals:
        if v not in seen:
            out.append(v); seen.add(v)
    return out

def show_one_pokemon(row, ability_cols, name_col, stat_cols):
    # 表示用テーブル
    rows = []
    labels = [("HP","hp"), ("攻撃","atk"), ("防御","def"), ("特攻","spa"), ("特防","spd"), ("素早さ","spe"), ("合計","bst")]
    for (label, key) in labels:
        colname = stat_cols.get(key)
        if colname and colname in row.index:
            rows.append({"項目": label, "値": row.get(colname, "")})
    st.subheader(f"📘 {row[name_col]}")
    if rows:
        st.table(pd.DataFrame(rows))
    abilities = extract_abilities(row, ability_cols)
    st.subheader("✨ 特性")
    if abilities:
        for ab in abilities:
            st.write(f"- {ab}")
    else:
        st.write("（特性情報なし）")

# ------------------------------
# CSV読み込み
# ------------------------------
try:
    df = pd.read_csv(CSV_PATH)
except Exception:
    df = pd.read_csv(CSV_PATH, encoding="cp932")

st.success(f"CSV読込 OK（{len(df)} 行, {len(df.columns)} 列）")

# 列名推定（最低限の前提：名前＋主要ステ）
cols = list(df.columns)
name_col = "名前" if "名前" in cols else cols[0]

def pick(cols, candidates):
    nmap = {c: normalize_text(c) for c in cols}
    for cand in candidates:
        nc = normalize_text(cand)
        for col, ncol in nmap.items():
            if nc == ncol:
                return col
    for cand in candidates:
        nc = normalize_text(cand)
        for col, ncol in nmap.items():
            if (nc in ncol) or (ncol in nc):
                return col
    return None

stat_cols = {
    "hp":  pick(cols, ["hp","ＨＰ","HP"]),
    "atk": pick(cols, ["攻撃","こうげき","atk"]),
    "def": pick(cols, ["防御","ぼうぎょ","def"]),
    "spa": pick(cols, ["特攻","とくこう","spa"]),
    "spd": pick(cols, ["特防","とくぼう","spd"]),
    "spe": pick(cols, ["素早さ","すばやさ","spe"]),
    "bst": pick(cols, ["合計","合計値","合計種族値","total","bst"]),
}

ability_cols = collect_ability_columns(cols)

# ------------------------------
# 検索UI（ボタンなし）
# ------------------------------
st.title("🔎 ポケモン 種族値・特性 検索（固定CSV版）")

q = st.text_input("ポケモン名を入力（部分一致OK・ボタン不要）", value="", key="query")

if q.strip():
    nq = normalize_text(q)
    names = df[name_col].fillna("").astype(str)
    mask = names.apply(lambda s: nq in normalize_text(s))
    cand = df[mask]

    count = len(cand)
    if count == 0:
        st.warning("ヒットしませんでした。表記を変えて再検索してみてください。")
    elif count == 1:
        show_one_pokemon(cand.iloc[0], ability_cols, name_col, stat_cols)
    else:
        st.info(f"{count}件ヒット。10件まではタブで切替えられます。11件以上はプルダウンで選択して表示します。")

        if count <= 10:
            labels = [str(v) for v in cand[name_col].astype(str).tolist()]
            tabs = st.tabs(labels)
            for tab, (_, row) in zip(tabs, cand.iterrows()):
                with tab:
                    show_one_pokemon(row, ability_cols, name_col, stat_cols)
        else:
            options = list(cand[name_col].astype(str))
            choice = st.selectbox("候補から選択", options=options, key="choice")
            picked = cand[cand[name_col].astype(str) == choice].iloc[0]
            show_one_pokemon(picked, ability_cols, name_col, stat_cols)
else:
    st.info("検索欄に名前を入力すると、候補と詳細がすぐに表示されます。")