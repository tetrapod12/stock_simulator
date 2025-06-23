import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import yfinance as yf
matplotlib.rcParams['font.family'] = 'Meiryo'

# タイトル
st.title("積立投資シミュレーター")

# 初期設定（積立額）
if "monthly_invest" not in st.session_state:
    st.session_state["monthly_invest"] = 15000

# 毎月の積立額（変更を検知してセッションに保存）
monthly_input = st.number_input("毎月の積立額（円）", value=st.session_state["monthly_invest"], step=1000)
if monthly_input != st.session_state["monthly_invest"]:
    st.session_state["monthly_invest"] = monthly_input

# ティッカー入力
ticker = st.text_input("ティッカーシンボル(例：AAPL)", value="AAPL")

# 株価取得期間
st.subheader("株価の取得期間")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("開始日", value=datetime(2020, 1, 1))
with col2:
    end_date = st.date_input("終了日", value=datetime.today())

# 株価データ取得ボタン
if st.button("株価データを取得"):
    raw = yf.download(ticker, start=start_date, end=end_date, interval="1mo")

    if raw.empty:
        st.error("データが取得できませんでした。ティッカーまたは期間を確認してください。")
    else:
        # マルチインデックスの場合に対応
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        # 'Adj Close' または 'Close' のどちらかを使用
        if "Adj Close" in raw.columns:
            df = raw[["Adj Close"]].reset_index()
            df.rename(columns={"Date": "年月", "Adj Close": "株価"}, inplace=True)
        elif "Close" in raw.columns:
            df = raw[["Close"]].reset_index()
            df.rename(columns={"Date": "年月", "Close": "株価"}, inplace=True)
        else:
            st.error("データに 'Adj Close' や 'Close' の列が含まれていません。別のティッカーを試すか、期間を見直してください。")
            st.stop()

        # 日付を年月に整形
        df["年月"] = pd.to_datetime(df["年月"]).dt.to_period("M").dt.to_timestamp()

        # セッションに保存して成功メッセージを表示
        st.session_state["df"] = df
        st.success(f"{ticker} の株価データ（{len(df)} 件）の取得に成功しました。")

# データが存在する場合に処理継続
if "df" in st.session_state:
    df = st.session_state["df"]
    st.subheader("シミュレーション表示期間の選択")
    min_date = df["年月"].min().to_pydatetime()
    max_date = df["年月"].max().to_pydatetime()
    simulation_range = st.slider("積立対象期間を選択", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM")

    sim_df = df[(df["年月"] >= simulation_range[0]) & (df["年月"] <= simulation_range[1])].copy()

    # 再取得した積立額
    monthly = st.session_state["monthly_invest"]

    sim_df["購入株数"] = monthly / sim_df["株価"]
    sim_df["累積株数"] = sim_df["購入株数"].cumsum()
    sim_df["累積投資額"] = monthly * (sim_df.index + 1)

    latest_price = sim_df["株価"].iloc[-1]
    sim_df["評価額"] = sim_df["累積株数"] * latest_price
    sim_df["含み損益"] = sim_df["評価額"] - sim_df["累積投資額"]

    num_points = len(sim_df)

    # 表示用に整数化
    display_df = sim_df.copy()
    display_df["購入株数"] = display_df["購入株数"].apply(lambda x: f"{x:,.0f}")
    display_df["累積株数"] = display_df["累積株数"].apply(lambda x: f"{x:,.0f}")
    display_df["評価額"] = display_df["評価額"].apply(lambda x: f"{x:,.0f}")
    display_df["含み損益"] = display_df["含み損益"].apply(lambda x: f"{x:,.0f}")

    st.write("積立投資シミュレーション結果：")
    st.dataframe(display_df)

    # グラフ（評価額 vs 投資額）
    fig_width = max(8, num_points * 0.3)
    fig, ax = plt.subplots(figsize=(fig_width, 5))
    ax.plot(sim_df["年月"], sim_df["累積投資額"], label="累積投資額", marker="o")
    ax.plot(sim_df["年月"], sim_df["評価額"], label="評価額", marker="o")
    ax.set_xlabel("年月")
    ax.set_ylabel("金額（円）")
    ax.legend()
    if num_points > 24:
        step = num_points // 12
        xticks = sim_df["年月"].iloc[::step]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks.dt.strftime("%Y-%m"), rotation=45)
    else:
        plt.xticks(rotation=45)
    st.subheader("投資額と評価額の推移")
    st.pyplot(fig)

    # グラフ（含み損益）
    fig2, ax2 = plt.subplots(figsize=(fig_width, 5))
    ax2.plot(sim_df["年月"], sim_df["含み損益"], color="green", marker="o")
    ax2.axhline(0, color="gray", linestyle="--")
    ax2.set_xlabel("年月")
    ax2.set_ylabel("含み損益（円）")
    if num_points > 24:
        xticks2 = sim_df["年月"].iloc[::step]
        ax2.set_xticks(xticks2)
        ax2.set_xticklabels(xticks2.dt.strftime("%Y-%m"), rotation=45)
    else:
        plt.xticks(rotation=45)
    st.subheader("含み損益の推移")
    st.pyplot(fig2)

    # メトリクス表示
    st.metric("最終評価額", f"¥{sim_df['評価額'].iloc[-1]:,.0f}")
    st.metric("含み損益", f"¥{sim_df['含み損益'].iloc[-1]:,.0f}")

    # 履歴保存
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if st.button("このシミュレーション結果を記録する"):
        record = {
            "積立額": monthly,
            "開始年月": simulation_range[0].strftime("%Y-%m"),
            "終了年月": simulation_range[1].strftime("%Y-%m"),
            "期間（月）": len(sim_df),
            "最終評価額": round(sim_df["評価額"].iloc[-1]),
            "含み損益": round(sim_df["含み損益"].iloc[-1]),
        }
        st.session_state["history"].append(record)
        st.success("結果を記録しました！")

    # 履歴表示
    if st.session_state["history"]:
        st.subheader("シミュレーション履歴")
        hist_df = pd.DataFrame(st.session_state["history"])
        st.dataframe(hist_df.style.format({
            "積立額": "¥{:,}",
            "最終評価額": "¥{:,}",
            "含み損益": "¥{:,}"
        }))

        if st.button("履歴をすべてクリアする"):
            st.session_state["history"] = []
            st.info("履歴をクリアしました。")
else:
    st.info("株価データを取得して下さい。")
