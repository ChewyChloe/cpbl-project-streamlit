import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json

st.set_page_config(page_title="球員介面", page_icon="🃏", layout="wide")

JSON_URL = "https://raw.githubusercontent.com/ChewyChloe/cpbl-project/refs/heads/main/player_commentary.json"
DATA_URL = "https://raw.githubusercontent.com/ChewyChloe/cpbl-project/d58371c954f80fac88be0eaf55943453dfe3ee0a/baseball_data.csv"

# 球員名單、照片
TARGET_PLAYERS = ['江坤宇', '林立', '陳冠宇', '陳傑憲']
PLAYER_PHOTOS = {
    '江坤宇': 'https://imgcdn.cna.com.tw/www/WebPhotos/800/20241001/824x1024_wmkn_0_C20241001000234.jpg',
    '林立': 'https://img.ltn.com.tw/Upload/sports/page/800/2023/12/22/120.jpg',
    '陳冠宇': 'https://hips.hearstapps.com/hmg-prod/images/pitcher-chen-kuan-yu-of-chinese-taipei-reacts-at-the-end-of-news-photo-1732522777.jpg',
    '陳傑憲': 'https://img.ltn.com.tw/Upload/sports/page/800/2025/06/04/121.jpg'
}
TEAM_FIX = {
    '江坤宇': '中信兄弟',
    '林立': '樂天桃猿',
    '陳冠宇': '樂天桃猿',
    '陳傑憲': '統一獅'
}

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        numeric_cols = ['bat_AVG', 'bat_OPS', 'bat_HR', 'bat_SB', 'bat_RBI',
                        'pit_ERA', 'pit_W', 'pit_SO', 'pit_WHIP', 'pit_IP']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    except Exception as e:
        return pd.DataFrame(), {}

    commentaries = {}
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            commentaries = response.json()
        else:
            alt_url = JSON_URL.replace("/refs/heads/main/", "/main/")
            response = requests.get(alt_url)
            if response.status_code == 200:
                commentaries = response.json()
    except Exception as e:
        pass

    return df, commentaries

# 雷達圖
def create_radar_chart(player_data):
    player_name = player_data['Name_clean']
    is_pitcher = player_data.get('pit_IP', 0) > 0

    fig = go.Figure()

    if is_pitcher:
        categories = ['勝投', '奪三振', '局數', '防禦率', 'WHIP']
        real_values = [
            player_data.get('pit_W', 0), player_data.get('pit_SO', 0), player_data.get('pit_IP', 0),
            player_data.get('pit_ERA', 0), player_data.get('pit_WHIP', 0)
        ]
        plot_values = [
            min(real_values[0] * 5, 100), min(real_values[1] * 0.5, 100), min(real_values[2] * 0.5, 100),
            max((5 - real_values[3]) * 20, 0), max((2 - real_values[4]) * 50, 0)
        ]
    else:
        categories = ['打擊率', 'OPS', '全壘打', '打點', '盜壘']
        real_values = [
            player_data.get('bat_AVG', 0), player_data.get('bat_OPS', 0), player_data.get('bat_HR', 0),
            player_data.get('bat_RBI', 0), player_data.get('bat_SB', 0)
        ]
        plot_values = [
            min(real_values[0] * 300, 100), min(real_values[1] * 100, 100), min(real_values[2] * 4, 100),
            min(real_values[3] * 1, 100), min(real_values[4] * 3, 100)
        ]

    fig.add_trace(go.Scatterpolar(
        r=plot_values,
        theta=categories,
        fill='toself',
        name=player_name,
        line_color='#FFD700',
        fillcolor='rgba(255, 215, 0, 0.3)',
        hovertemplate="%{theta}: <b>%{text}</b><extra></extra>",
        text=[f"{v:.2f}" if isinstance(v, float) else v for v in real_values]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(color='rgba(255,255,255,0.7)', size=9),
                gridcolor='rgba(255, 255, 255, 0.2)',
                linecolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                visible=True,
                tickfont=dict(color='#FFD700', size=14, weight='bold'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        height=300,
        margin=dict(t=40, b=20, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

# 佈局
st.title("🃏球員介紹卡牌")

st.markdown("""
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #1e1e2f, #2a2a40);
    border: 2px solid #FFD700 !important;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
}
div[data-testid="stVerticalBlockBorderWrapper"] * {
    color: white !important;
}
.stTabs [data-baseweb="tab-list"] { background-color: transparent; }
.stTabs [aria-selected="true"] { color: #FFD700 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

df, commentaries = load_data()

if df.empty:
    st.error("⚠️ 無法讀取資料")
    st.stop()

df_players = df[df['Name_clean'].isin(TARGET_PLAYERS)].copy()
df_players = df_players.sort_values('Year', ascending=False).drop_duplicates(subset='Name_clean', keep='first')

st.divider()

cols = st.columns(2) + st.columns(2)

count = 0
for i, player_name in enumerate(TARGET_PLAYERS):
    if i >= 4: break

    col = cols[i]
    rows = df_players[df_players['Name_clean'] == player_name]

    if rows.empty:
        col.warning(f"缺失 {player_name}")
        continue

    data = rows.iloc[0]
    comment = commentaries.get(player_name,)
    fig = create_radar_chart(data)
    photo = PLAYER_PHOTOS.get(player_name, "")

    # 判斷身分
    role = "投手" if data.get('pit_IP', 0) > 0 else "打擊手"

    # 判斷隊名
    team_name = data.get('Team Name_x')
    if pd.isna(team_name) or str(team_name).lower() == 'nan':
        team_name = TEAM_FIX.get(player_name, "CPBL")

    with col:
        with st.container(height=600, border=True):
            st.subheader(player_name)
            st.caption(f"{team_name} | {role}")

            t1, t2 = st.tabs(["📷 照片", "📊 分析"])

            with t1:
                if photo: st.image(photo, use_container_width=True)
                else: st.info("無照片")

            with t2:
                st.markdown("#### 🧐 AI 球評")
                st.info(comment)
                st.markdown("#### 𖣠 能力雷達")
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    count += 1

if count == 0:
    st.warning("沒有顯示任何卡牌")
