import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath('.'))
try:
    from shared import styles
    styles.apply_global_style()
except ImportError:
    pass

st.set_page_config(page_title="深度數據論壇", layout="wide")

st.markdown("""
    <style>
    /* 確保樣式正確 */
    section[data-testid="stSidebar"] { background-color: #001844 !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
        color: #000000 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 深度數據論壇")
st.markdown("### ⚾ Sabermetrics：用進階數據看棒球")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('baseball_data.csv')
    except FileNotFoundError:
        st.error("找不到資料檔")
        return pd.DataFrame()

    numeric_cols = [
        'bat_PA', 'bat_AB', 'bat_R', 'bat_H', 'bat_2B', 'bat_3B', 'bat_HR',
        'bat_SF', 'bat_SH', 'bat_BB', 'bat_IBB', 'bat_HBP',
        'bat_SO', 'bat_SB', 'bat_CS', 'bat_GIDP',
        'bat_AVG', 'bat_OPS'
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # 計算
    # 一壘安打 (1B) = H - 2B - 3B - HR
    if 'bat_H' in df.columns and 'bat_2B' in df.columns:
        df['bat_1B'] = df['bat_H'] - df['bat_2B'] - df['bat_3B'] - df['bat_HR']
    else:
        df['bat_1B'] = 0

    team_map = {
        '統一獅': '統一7-ELEVEn獅', '統一': '統一7-ELEVEn獅',
        '桃猿': '樂天桃猿', 'Lamigo': '樂天桃猿', 'Rakuten': '樂天桃猿',
        '兄弟': '中信兄弟', '兄弟象': '中信兄弟',
        '富邦': '富邦悍將', '義大': '富邦悍將',
        '味全': '味全龍', '台鋼': '台鋼雄鷹'
    }
    target_teams = ['統一7-ELEVEn獅', '台鋼雄鷹', '中信兄弟', '樂天桃猿', '味全龍', '富邦悍將']

    cols_needed = [
        'Name_clean', 'Team Name_x', 'Year',
        'bat_PA', 'bat_AB', 'bat_R', 'bat_H', 'bat_1B', 'bat_BB', 'bat_HBP', 'bat_IBB',
        'bat_SF', 'bat_AVG', 'bat_OPS', 'bat_SB', 'bat_CS'
    ]
    valid_cols = [c for c in cols_needed if c in df.columns]

    df_sorted = df[valid_cols].sort_values(by=['Year', 'bat_PA'], ascending=[False, False])
    df_bat = df_sorted.drop_duplicates(subset=['Name_clean', 'Year'], keep='first')

    rename_dict = {
        'Name_clean': 'Name', 'Team Name_x': 'Team',
        'bat_OPS': 'OPS', 'bat_AVG': 'AVG',
        'bat_SB': 'SB', 'bat_CS': 'CS', 'bat_PA': 'PA',
        'bat_1B': '1B', 'bat_BB': 'BB', 'bat_HBP': 'HBP', 'bat_IBB': 'IBB',
        'bat_R': 'R', 'bat_AB': 'AB', 'bat_H': 'H', 'bat_SF': 'SF'
    }
    df_bat = df_bat.rename(columns={k:v for k,v in rename_dict.items() if k in df_bat.columns})

    df_bat['Team'] = df_bat['Team'].replace(team_map)
    df_bat = df_bat[df_bat['Team'].isin(target_teams)]
    df_bat = df_bat[df_bat['PA'] > 0]

    return df_bat

df = load_data()

if df.empty:
    st.stop()

# 議題選擇
topic = st.radio(
    "請選擇想要探討的議題：",
    ["📉 議題一：打擊率 (AVG) 是不是過時了？", "🏃 議題二：盜壘價值 (wSB) 的應用"],
    horizontal=True
)

st.divider()

# 議題一：打擊率 vs OPS
if "議題一" in topic:
    st.header("📉 打擊率 (AVG) vs 整體攻擊指數 (OPS)")
    st.markdown("""
    **傳統觀點**：打擊率 (AVG) 是衡量打者好壞的最重要指標。
    **數據觀點**：打擊率忽略了「選球眼 (保送)」和「長打能力 (全壘打)」，打擊率高的球員貢獻度可能不如打擊率低者。
    """)

    col1, col2 = st.columns(2)
    sel_year = col1.selectbox("選擇年份", sorted(df['Year'].unique(), reverse=True))
    min_pa = col2.slider("過濾：最少打席數 (PA)", 0, 500, 100)

    df_topic1 = df[(df['Year'] == sel_year) & (df['PA'] >= min_pa)].copy()

    if not df_topic1.empty:
        corr = df_topic1['AVG'].corr(df_topic1['OPS'])
        st.info(f"💡 **數據發現**：在 {sel_year} 年，打擊率與 OPS 的相關係數為 **{corr:.2f}**。")

        fig = px.scatter(
            df_topic1, x='AVG', y='OPS',
            color='Team', size='PA', hover_name='Name',
            text='Name',
            title=f"{sel_year} 年打者分佈：AVG vs OPS"
        )
        avg_mean = df_topic1['AVG'].mean()
        ops_mean = df_topic1['OPS'].mean()
        fig.add_vline(x=avg_mean, line_dash="dash", line_color="gray", annotation_text="平均AVG")
        fig.add_hline(y=ops_mean, line_dash="dash", line_color="gray", annotation_text="平均OPS")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("此條件下無資料。")

# 議題二：盜壘運用
elif "議題二" in topic:
    st.header("🏃 盜壘分析")

    st.markdown("""
    我們採用 **FanGraphs** 的 **wSB** 公式來計算盜壘對球隊的真實得分貢獻。

    $$
    wSB = (SB \\times runSB) + (CS \\times runCS) - (lgwSB \\times (1B + BB + HBP - IBB))
    $$

    * **runSB (0.2)**：盜壘成功的得分期望值。
    * **runCS (約 -0.4)**：盜壘失敗的扣分，根據當年度的得分環境動態計算。
    * **lgwSB**：聯盟平均值，用來扣除「平均跑者在同樣上壘機會下應有的貢獻」。
    """)

    # 篩選
    col1, col2 = st.columns(2)
    sel_years = col1.multiselect("選擇年份", sorted(df['Year'].unique(), reverse=True), default=[2024, 2025] if 2024 in df['Year'].unique() else [df['Year'].max()])
    min_sb_attempt = col2.slider("過濾：最少嘗試盜壘次數 (SB+CS)", 0, 30, 5)

    df_topic2 = df[df['Year'].isin(sel_years)].copy()

    # 計算 wSB 參數
    if not df_topic2.empty:
        # 計算聯盟總和
        lg_R = df_topic2['R'].sum()
        # 估算 Outs (Outs = AB - H + CS + SF)
        lg_Outs = (df_topic2['AB'].sum() - df_topic2['H'].sum()) + df_topic2['CS'].sum() + df_topic2['SF'].sum()
        if lg_Outs == 0: lg_Outs = 1

        # 動態計算 runCS (FanGraphs 公式: 2 * R/Outs + 0.075)
        runs_per_out = lg_R / lg_Outs
        runSB = 0.2
        runCS = -1 * (2 * runs_per_out + 0.075)

        # 計算 lgwSB
        lg_SB = df_topic2['SB'].sum()
        lg_CS = df_topic2['CS'].sum()
        # 上壘機會 (Singles + BB + HBP - IBB)
        lg_1B = df_topic2['1B'].sum()
        lg_BB = df_topic2['BB'].sum()
        lg_HBP = df_topic2['HBP'].sum()
        lg_IBB = df_topic2['IBB'].sum()

        lg_opportunities = lg_1B + lg_BB + lg_HBP - lg_IBB
        if lg_opportunities == 0: lg_opportunities = 1

        lgwSB = (lg_SB * runSB + lg_CS * runCS) / lg_opportunities

        def calculate_wSB(row):
            opportunities = row['1B'] + row['BB'] + row['HBP'] - row['IBB']
            # wSB
            val = (row['SB'] * runSB) + (row['CS'] * runCS) - (lgwSB * opportunities)
            return val

        df_topic2['wSB'] = df_topic2.apply(calculate_wSB, axis=1)
        df_topic2['Attempt'] = df_topic2['SB'] + df_topic2['CS']

        # 過濾
        df_filtered = df_topic2[df_topic2['Attempt'] >= min_sb_attempt].copy()
        df_filtered['SB_Rate'] = df_filtered.apply(lambda x: (x['SB']/x['Attempt']*100) if x['Attempt']>0 else 0, axis=1)

        st.info(f"📊 **本期參數**：runCS (失敗扣分) = **{runCS:.3f}** (約為成功的 {abs(runCS/runSB):.1f} 倍代價)")

        # 表 1: wSB 排行榜
        st.subheader("🏆 wSB 排行榜：誰是真正的盜壘貢獻王？")
        st.caption("wSB > 0 代表比聯盟平均跑者貢獻更多分數；wSB < 0 代表拖累球隊。")

        top_n = 10
        df_rank = df_filtered.sort_values('wSB', ascending=True).tail(top_n)
        df_bottom = df_filtered.sort_values('wSB', ascending=True).head(5)
        df_chart = pd.concat([df_bottom, df_rank]).drop_duplicates().sort_values('wSB')

        colors = ['red' if x < 0 else '#2E5090' for x in df_chart['wSB']]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_chart['Name'], x=df_chart['wSB'],
            orientation='h', marker_color=colors,
            text=df_chart['wSB'].apply(lambda x: f"{x:.2f}"),
            textposition='auto',
            hovertemplate="<b>%{y}</b><br>SB: %{customdata[0]}<br>CS: %{customdata[1]}<br>wSB: %{x:.2f}<extra></extra>",
            customdata=df_chart[['SB', 'CS']]
        ))
        fig.update_layout(title="Weighted Stolen Base Runs (wSB)", xaxis_title="wSB (分數貢獻)", height=600)
        st.plotly_chart(fig, use_container_width=True)

        # 表 2：高成功率不代表高貢獻
        st.subheader("📉 成功率 vs wSB：高成功率不代表高貢獻")
        fig2 = px.scatter(
            df_filtered, x='SB_Rate', y='wSB',
            color='Team', size='Attempt', hover_name='Name',
            text='Name',
            labels={'SB_Rate': '盜壘成功率 (%)', 'wSB': 'wSB (得分貢獻)'},
            title="有些球員成功率高(右邊)，但因為跑得少或機會成本高，wSB 其實不高"
        )
        fig2.add_hline(y=0, line_dash="solid", line_color="gray")
        fig2.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="75% 及格線")
        st.plotly_chart(fig2, use_container_width=True)

        # 結論
        best = df_filtered.loc[df_filtered['wSB'].idxmax()]
        worst = df_filtered.loc[df_filtered['wSB'].idxmin()]

        st.success(f"🥇 **最佳跑者**：**{best['Name']}** (wSB {best['wSB']:.2f})。他在扣除失敗風險與機會成本後，依然為球隊創造了顯著價值。")
        if worst['wSB'] < 0:
            st.error(f"⚠️ **負分跑者**：**{worst['Name']}** (wSB {worst['wSB']:.2f})。雖然他可能跑了不少，但相對於聯盟平均，他的跑壘策略其實是在減少球隊得分期望值。")

    else:
        st.warning("⚠️ 此條件下無資料")
