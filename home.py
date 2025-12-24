import streamlit as st
import os
import sys

st.set_page_config(layout='wide', page_title='CPBL 棒球分析系統')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from shared.styles import apply_global_style
    from shared.resources import load_resources
    apply_global_style()
    model, df_stats = load_resources()
except ImportError:
    st.warning("⚠️ 無法載入樣式或資源")

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
