import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import json

DATA_FILE = "typing_data.json"

st.set_page_config(page_title="タイピング成績トラッカー", page_icon="⌨️", layout="wide")

# ---- データ管理 ----

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        return df
    return pd.DataFrame(columns=["date", "wpm", "accuracy", "score", "mode", "memo"])


def save_record(record: dict):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []
    records.append(record)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def delete_record(index: int):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
    records.pop(index)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ---- UI ----

st.title("⌨️ タイピング成績トラッカー")

df = load_data()

tab_input, tab_graph, tab_history = st.tabs(["📝 結果を入力", "📊 グラフ", "📋 履歴"])

# ========== 入力タブ ==========
with tab_input:
    st.subheader("新しい結果を記録")
    col1, col2 = st.columns(2)

    with col1:
        date_val = st.date_input("日付", value=datetime.today())
        wpm = st.number_input("WPM（1分間の打鍵数）", min_value=0, max_value=1000, value=0, step=1)
        accuracy = st.slider("正確率 (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1)

    with col2:
        score = st.number_input("スコア", min_value=0, value=0, step=1)
        mode = st.selectbox("モード / サイト", ["e-typing", "寿司打", "タイピング天国", "monkeytype", "その他"])
        memo = st.text_input("メモ（任意）", placeholder="例: 今日は調子良かった")

    if st.button("記録する", type="primary", use_container_width=True):
        record = {
            "date": datetime.combine(date_val, datetime.min.time()).isoformat(),
            "wpm": wpm,
            "accuracy": round(accuracy, 1),
            "score": score,
            "mode": mode,
            "memo": memo,
        }
        save_record(record)
        st.success("記録しました！")
        st.rerun()

# ========== グラフタブ ==========
with tab_graph:
    if df.empty:
        st.info("まだデータがありません。「結果を入力」タブから記録してください。")
    else:
        df_sorted = df.sort_values("date")

        # フィルタ
        modes = ["すべて"] + sorted(df["mode"].unique().tolist())
        selected_mode = st.selectbox("モードで絞り込み", modes)
        plot_df = df_sorted if selected_mode == "すべて" else df_sorted[df_sorted["mode"] == selected_mode]

        if plot_df.empty:
            st.warning("選択したモードのデータがありません。")
        else:
            col_g1, col_g2 = st.columns(2)

            # WPM 推移
            with col_g1:
                fig_wpm = px.line(
                    plot_df, x="date", y="wpm",
                    markers=True,
                    title="WPM 推移",
                    labels={"date": "日付", "wpm": "WPM"},
                    color="mode" if selected_mode == "すべて" else None,
                )
                fig_wpm.update_traces(line_width=2, marker_size=7)
                fig_wpm.update_layout(hovermode="x unified")
                st.plotly_chart(fig_wpm, use_container_width=True)

            # 正確率 推移
            with col_g2:
                fig_acc = px.line(
                    plot_df, x="date", y="accuracy",
                    markers=True,
                    title="正確率 推移 (%)",
                    labels={"date": "日付", "accuracy": "正確率 (%)"},
                    color="mode" if selected_mode == "すべて" else None,
                )
                fig_acc.update_traces(line_width=2, marker_size=7)
                fig_acc.update_layout(yaxis_range=[0, 100], hovermode="x unified")
                st.plotly_chart(fig_acc, use_container_width=True)

            col_g3, col_g4 = st.columns(2)

            # スコア 推移
            with col_g3:
                fig_score = px.bar(
                    plot_df, x="date", y="score",
                    title="スコア 推移",
                    labels={"date": "日付", "score": "スコア"},
                    color="mode" if selected_mode == "すべて" else None,
                )
                fig_score.update_layout(hovermode="x unified")
                st.plotly_chart(fig_score, use_container_width=True)

            # WPM vs 正確率 散布図
            with col_g4:
                fig_scatter = px.scatter(
                    plot_df, x="wpm", y="accuracy",
                    title="WPM vs 正確率",
                    labels={"wpm": "WPM", "accuracy": "正確率 (%)"},
                    color="mode",
                    hover_data=["date", "score", "memo"],
                    size_max=12,
                )
                fig_scatter.update_traces(marker_size=10)
                fig_scatter.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_scatter, use_container_width=True)

            # サマリー統計
            st.subheader("サマリー統計")
            summary_cols = st.columns(4)
            stats = {
                "最高WPM": int(plot_df["wpm"].max()),
                "平均WPM": round(plot_df["wpm"].mean(), 1),
                "平均正確率": f"{round(plot_df['accuracy'].mean(), 1)}%",
                "最高スコア": int(plot_df["score"].max()),
            }
            for col, (label, val) in zip(summary_cols, stats.items()):
                col.metric(label, val)

# ========== 履歴タブ ==========
with tab_history:
    if df.empty:
        st.info("まだデータがありません。")
    else:
        df_display = df.sort_values("date", ascending=False).copy()
        df_display["date"] = df_display["date"].dt.strftime("%Y-%m-%d")
        df_display.columns = ["日付", "WPM", "正確率(%)", "スコア", "モード", "メモ"]
        df_display = df_display.reset_index(drop=True)

        st.dataframe(df_display, use_container_width=True, hide_index=False)

        st.divider()
        st.subheader("レコードを削除")
        del_index = st.number_input(
            "削除する行番号（上の表の左端の番号）",
            min_value=0, max_value=max(0, len(df) - 1), step=1
        )
        # 表示順（降順）→ 元データのインデックスに変換
        original_indices = df.sort_values("date", ascending=False).index.tolist()
        if st.button("削除する", type="secondary"):
            actual_idx = original_indices[del_index]
            delete_record(actual_idx)
            st.success(f"行 {del_index} を削除しました。")
            st.rerun()
