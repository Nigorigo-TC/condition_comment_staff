from datetime import date

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="無料版コンディションコメントアプリ",
    page_icon="📝",
    layout="centered",
)

st.title("無料版コンディションコメントアプリ")
st.caption("画面には名前表示 / コメントはルールベースで自動生成")


EXCEL_FILE = "condition_demo.xlsx"


@st.cache_data
def load_data():
    athletes_df = pd.read_excel(EXCEL_FILE, sheet_name="athletes")
    records_df = pd.read_excel(EXCEL_FILE, sheet_name="records")
    return athletes_df, records_df


def make_comment(general_condition, fatigue, sleep_depth, appetite, spo2, pulse, special_notes):
    comments = []
    checks = []

    # 総合状態
    if general_condition <= 30:
        comments.append("全般的な体調はかなり低めです。")
        checks.append("体調確認を優先してください。")
    elif general_condition <= 50:
        comments.append("全般的な体調はやや低めです。")

    # 疲労
    if fatigue >= 80:
        comments.append("疲労感がかなり高い状態です。")
        checks.append("練習前の状態確認を推奨します。")
    elif fatigue >= 70:
        comments.append("疲労感が高めです。")

    # 睡眠
    if sleep_depth <= 30:
        comments.append("睡眠の質がかなり低めです。")
    elif sleep_depth <= 40:
        comments.append("睡眠の質がやや低めです。")

    # 食欲
    if appetite <= 30:
        comments.append("食欲低下がみられます。")
    elif appetite <= 40:
        comments.append("食欲がやや低めです。")

    # SpO2
    if spo2 <= 90:
        comments.append("SpO2が低めです。")
        checks.append("高地適応や体調変化の確認が必要です。")
    elif spo2 <= 92:
        comments.append("SpO2がやや低めです。")

    # 脈拍
    if pulse >= 80:
        comments.append("脈拍数が高めです。")
        checks.append("回復状況の確認を推奨します。")

    # 特記事項
    if "頭痛" in special_notes:
        comments.append("頭痛の申告があります。")
        checks.append("症状の継続有無を確認してください。")

    if "咳" in special_notes or "のどの痛み" in special_notes or "倦怠感" in special_notes:
        comments.append("体調変化を示す症状の申告があります。")
        checks.append("感染兆候を含めた状態確認を推奨します。")

    if "下痢" in special_notes or "腹痛" in special_notes or "吐き気" in special_notes:
        comments.append("消化器症状の申告があります。")
        checks.append("食事・水分摂取状況も確認してください。")

    if not comments:
        return "大きな問題は目立たず、概ね安定しています。"

    text = " ".join(comments)

    if checks:
        unique_checks = []
        for c in checks:
            if c not in unique_checks:
                unique_checks.append(c)
        text += " " + unique_checks[0]

    return text


try:
    athletes_df, records_df = load_data()
except FileNotFoundError:
    st.error("condition_demo.xlsx が見つかりません。GitHubにアップロードしてください。")
    st.stop()
except ValueError:
    st.error("Excel内に athletes シート または records シートがありません。")
    st.stop()


if "active" in athletes_df.columns:
    athletes_df = athletes_df[athletes_df["active"].astype(str).str.upper() == "TRUE"]

if athletes_df.empty:
    st.error("athletes シートに有効な選手がいません。")
    st.stop()


athletes_df["label"] = athletes_df.apply(
    lambda row: f'{row["display_name"]}（{row["athlete_id"]} / {row["team_name"]}）',
    axis=1
)

selected_label = st.selectbox("選手を選んでください", athletes_df["label"].tolist())
selected_row = athletes_df[athletes_df["label"] == selected_label].iloc[0]

athlete_id = selected_row["athlete_id"]
display_name = selected_row["display_name"]
team_name = selected_row["team_name"]


st.subheader("今日の入力")

input_date = st.date_input("日付", value=date.today())
general_condition = st.slider("全般的な体調（0=悪い, 100=良い）", 0, 100, 60)
fatigue = st.slider("疲労感（0=無い, 100=強い）", 0, 100, 50)
sleep_depth = st.slider("睡眠の深さ（0=浅い, 100=深い）", 0, 100, 50)
appetite = st.slider("食欲（0=無い, 100=ある）", 0, 100, 60)
spo2 = st.number_input("SpO2", min_value=0, max_value=100, value=95, step=1)
pulse = st.number_input("脈拍数", min_value=0, value=60, step=1)

special_notes = st.multiselect(
    "特記事項",
    ["特になし", "咳", "鼻水", "頭痛", "下痢", "のどの痛み", "腹痛", "倦怠感", "吐き気"]
)

st.subheader("参考：過去データ")
athlete_history = records_df[records_df["athlete_id"] == athlete_id].copy()

if not athlete_history.empty:
    if "date" in athlete_history.columns:
        athlete_history = athlete_history.sort_values("date", ascending=False)
    st.dataframe(athlete_history.head(5), use_container_width=True)
else:
    st.info("この選手の過去データはまだありません。")

if st.button("コメント生成", type="primary"):
    comment = make_comment(
        general_condition=general_condition,
        fatigue=fatigue,
        sleep_depth=sleep_depth,
        appetite=appetite,
        spo2=spo2,
        pulse=pulse,
        special_notes=special_notes,
    )

    st.success("コメントを生成しました")
    st.write(f"**{display_name}（{athlete_id} / {team_name}）**")
    st.write(comment)
