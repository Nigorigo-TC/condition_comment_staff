import json
from datetime import date

import pandas as pd
import streamlit as st
from openai import OpenAI


# -----------------------------
# 画面の基本設定
# -----------------------------
st.set_page_config(
    page_title="コンディション自動コメントデモ",
    page_icon="📝",
    layout="centered",
)

st.title("コンディション自動コメントデモ")
st.caption("スタッフ向けデモ版：画面には名前表示、AIにはID中心で送信")


# -----------------------------
# OpenAIクライアント
# Streamlit secrets に OPENAI_API_KEY を入れておく
# -----------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("OPENAI_API_KEY が設定されていません。Streamlit の Secrets に登録してください。")
    st.stop()


# -----------------------------
# Excel読み込み
# condition_demo.xlsx の中に
# athletes シートと records シートを作る
# -----------------------------
EXCEL_FILE = "condition_demo.xlsx"

@st.cache_data
def load_data():
    athletes_df = pd.read_excel(EXCEL_FILE, sheet_name="athletes")
    records_df = pd.read_excel(EXCEL_FILE, sheet_name="records")
    return athletes_df, records_df


try:
    athletes_df, records_df = load_data()
except FileNotFoundError:
    st.error("condition_demo.xlsx が見つかりません。GitHubにアップしてください。")
    st.stop()
except ValueError:
    st.error("Excelファイルに athletes シート または records シート がありません。")
    st.stop()


# -----------------------------
# active == TRUE の選手だけ表示
# -----------------------------
if "active" in athletes_df.columns:
    athletes_df = athletes_df[athletes_df["active"].astype(str).str.upper() == "TRUE"]

if athletes_df.empty:
    st.error("athletesシートに有効な選手データがありません。")
    st.stop()


# -----------------------------
# 選手選択用の表示文字列を作る
# 画面では「山田太郎（A001 / 長距離）」と見せる
# 内部では athlete_id を使う
# -----------------------------
athletes_df["label"] = athletes_df.apply(
    lambda row: f'{row["display_name"]}（{row["athlete_id"]} / {row.get("team_name", "")}）',
    axis=1
)

selected_label = st.selectbox(
    "選手を選んでください",
    athletes_df["label"].tolist()
)

selected_row = athletes_df[athletes_df["label"] == selected_label].iloc[0]
athlete_id = selected_row["athlete_id"]
display_name = selected_row["display_name"]
team_name = selected_row.get("team_name", "")


st.subheader("今日の入力")

input_date = st.date_input("日付", value=date.today())
general_condition = st.slider("全般的な体調（0=悪い, 100=良い）", 0, 100, 60)
fatigue = st.slider("疲労感（0=無い, 100=強い）", 0, 100, 50)
sleep_depth = st.slider("睡眠の深さ（0=浅い, 100=深い）", 0, 100, 50)
appetite = st.slider("食欲（0=無い, 100=ある）", 0, 100, 60)
injury_level = st.slider("故障の程度（0=痛み無い, 100=練習できない）", 0, 100, 0)
training_intensity = st.slider("練習強度（0=楽, 100=きつい）", 0, 100, 60)

sleep_hours = st.number_input("睡眠時間（時間）", min_value=0.0, max_value=24.0, value=7.0, step=0.5)

sleep_status = st.selectbox(
    "睡眠状況",
    [
        "特になし",
        "夢を見た",
        "何回も目覚めた",
        "何回もトイレに行った",
        "寝汗をかいた",
        "寝付けなかった",
        "普段より寝付けなかった",
    ]
)

injury_flag = st.radio("故障の有無", ["無", "有"], horizontal=True)
injury_site = st.text_input("故障の箇所（故障ありの場合）", value="")

bowel_flag = st.radio("排便の有無", ["無", "有"], horizontal=True)
stool_form = st.number_input("便の形（1-7）", min_value=1, max_value=7, value=4, step=1)

running_distance = st.number_input("走行距離", min_value=0.0, value=0.0, step=0.1)
spo2 = st.number_input("SpO2", min_value=0, max_value=100, value=95, step=1)
pulse = st.number_input("脈拍数", min_value=0, value=60, step=1)
temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
weight = st.number_input("体重", min_value=0.0, value=60.0, step=0.1)
weight_change_pct = st.number_input("体重変化率（前日からの%）", value=0.0, step=0.1)

special_notes = st.multiselect(
    "特記事項",
    [
        "特になし",
        "咳",
        "鼻水",
        "頭痛",
        "息苦しさ",
        "下痢",
        "のどの痛み",
        "悪寒",
        "腹痛",
        "熱感",
        "倦怠感",
        "吐き気",
        "痰",
        "月経",
        "月経痛",
        "月経前不調",
        "不正出血",
        "服薬",
        "その他",
    ]
)


# -----------------------------
# recordsシートから、その選手の最近データを取る
# 最初は「参考表示」だけ
# 後で推移コメントにも使える
# -----------------------------
st.subheader("参考：過去データ")

athlete_history = records_df[records_df["athlete_id"] == athlete_id].copy()

if not athlete_history.empty:
    if "date" in athlete_history.columns:
        athlete_history = athlete_history.sort_values("date", ascending=False)
    st.dataframe(athlete_history.head(5), use_container_width=True)
else:
    st.info("この選手の過去データはまだありません。")


# -----------------------------
# AIへ送るデータを作る
# 名前は送らない
# IDと数値・状態だけ送る
# -----------------------------
payload = {
    "date": str(input_date),
    "athlete_id": athlete_id,
    "general_condition": general_condition,
    "fatigue": fatigue,
    "sleep_depth": sleep_depth,
    "appetite": appetite,
    "injury_level": injury_level,
    "training_intensity": training_intensity,
    "sleep_hours": sleep_hours,
    "sleep_status": sleep_status,
    "injury_flag": injury_flag,
    "injury_site": injury_site,
    "bowel_flag": bowel_flag,
    "stool_form": stool_form,
    "running_distance": running_distance,
    "spo2": spo2,
    "pulse": pulse,
    "temperature": temperature,
    "weight": weight,
    "weight_change_pct": weight_change_pct,
    "special_notes": special_notes,
}


# -----------------------------
# コメント生成ボタン
# -----------------------------
if st.button("コメント生成", type="primary"):
    with st.spinner("コメントを生成しています..."):
        try:
            prompt = f"""
あなたはスポーツ現場のスタッフ向けに、朝のコンディション情報から短いコメントを作成するアシスタントです。

ルール:
- 出力は日本語
- 80〜140字程度
- スタッフ向けに簡潔に書く
- 医学的な断定はしない
- 状態の要点と、必要なら確認ポイントを1つ書く
- 選手名は書かない
- 与えられた情報だけをもとに書く
- 問題が大きくなければ過度に不安をあおらない

入力データ:
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""

            response = client.responses.create(
                model="gpt-5.4",
                input=prompt
            )

            comment = response.output_text

            st.success("コメント生成が完了しました")

            st.subheader("表示用（スタッフ画面）")
            st.write(f"**{display_name}（{athlete_id} / {team_name}）**")

            st.subheader("自動コメント")
            st.write(comment)

            st.subheader("AIに送った内容（確認用）")
            st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")

        except Exception as e:
            st.error(f"コメント生成中にエラーが発生しました: {e}")
