import streamlit as st
import os
import sys

st.set_page_config(layout='wide', page_title='CPBL 棒球分析系統')

custom_css = """
<style>
/* 全局 */
.stApp { background-color: #F8F9FA; }

/* 側欄 */
section[data-testid="stSidebar"] {
    background-color: #001844 !important;
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* 下拉選單 */
div[data-baseweb="select"] > div,
input[type="number"]{
  color:white !important;
  background-color:#002D62 !important;
  border-radius:5px;
}
ul[data-baseweb="menu"] li{
  color:black !important;
}

.stSelectbox label, .stNumberInput label, .stSlider label{
  color:#333333 !important;
  font-weight:bold;
}

/* 隱藏原生元件 */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

/* 團隊卡與 Podcast 卡 */
.podcast-card{
  background-color:#FFFFFF;
  border-radius:12px;
  box-shadow:0 4px 12px rgba(0,0,0,0.08);
  padding:15px;
  margin-bottom:20px;
  border:1px solid #e0e0e0;
  transition:transform 0.2s, box-shadow 0.2s;
  display:flex;
  flex-direction:column;
  align-items:center;
  text-align:center;
}
.podcast-card:hover{
  transform:translateY(-5px);
  box-shadow:0 8px 20px rgba(0,0,0,0.15);
}
.podcast-card h3{
  color:#001844;
  font-size:18px;
  font-weight:700;
  margin-top:15px;
  margin-bottom:5px;
  text-align:center;
}
.video-container{
  position:relative;
  width:100%;
  padding-bottom:56.25%;
  height:0;
  overflow:hidden;
  border-radius:8px;
}
.video-container iframe{
  position:absolute;
  top:0; left:0;
  width:100%;
  height:100%;
  border:0;
}

/* 開發團隊 */
.team-card{
  background-color:#FFF5F7;
  border:2px solid #FFD1DC;
  border-radius:20px;
  padding:20px;
  text-align:center;
  margin-bottom:20px;
  box-shadow:0 4px 10px rgba(255,182,193,0.2);
  transition:transform 0.3s ease;
  height: 100%;
}
.team-card:hover{
  transform:translateY(-5px);
  box-shadow:0 8px 15px rgba(255,182,193,0.5);
}
.team-name{
  color:#001844;
  font-size:20px;
  font-weight:bold;
  margin-bottom:5px;
}
.team-info{
  color:#666;
  font-size:14px;
  margin:2px 0;
}

/* AI 對話框 */
textarea[data-testid="stChatInputTextArea"] {
    color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
}
textarea[data-testid="stChatInputTextArea"]::placeholder {
    color: #DDDDDD !important;
    opacity: 1;
}
</style>
"""

def apply_global_style():
    st.markdown(custom_css, unsafe_allow_html=True)

apply_global_style()

st.title("CPBL 棒球分析系統")

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from shared.resources import load_resources
    model, df_stats = load_resources()
except Exception:
    pass

# 主頁
st.markdown("""
<div style="background-color: #001844; padding: 2rem; border-radius: 1rem; color: white; margin-bottom: 2rem;">
    <h1 style='color: white; margin:0;'>CPBL 棒球分析系統</h1>
    <p style='color: #cbd5e1; margin-top: 10px;'>帶你一起認識棒球!!</p>
</div>
""", unsafe_allow_html=True)

# 數據指標
m1, m2, m3 = st.columns(3)
m1.metric("模型準確率", "95.9%", "高準確率")
m2.metric("已執行預測", "761 場", "場場收錄")
m3.metric("歷史數據庫", "35 年", "年年都有")

st.markdown("### 🎧 相關影片")

podcasts = [
    {"title": "棒球報你知 Podcast EP.1 中職建軍大洗牌", "video_id": "68C5TK90YGk"},
    {"title": "台灣大賽 Game 5 總冠軍賽精華片段", "video_id": "emVgQV6UyIM"}
]

cols = st.columns(len(podcasts) if len(podcasts) > 0 else 1)
if len(podcasts) == 1:
    cols = [st.columns([1, 2, 1])[1]]

for i, podcast in enumerate(podcasts):
    with cols[i]:
        embed_url = f"https://www.youtube.com/embed/{podcast['video_id']}"
        st.video(f"https://www.youtube.com/watch?v={podcast['video_id']}")
        st.caption(podcast['title'])
