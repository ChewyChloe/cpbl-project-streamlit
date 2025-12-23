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
except ImportError:
    pass

st.set_page_config(page_title="CPBL 數據儀表板", layout="wide")
st.title("⚾ CPBL 職棒數據分析中心")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('baseball_data.csv')
    except FileNotFoundError:
        st.error("找不到 'baseball_data.csv'")
        return pd.DataFrame(), pd.DataFrame()

    cols_to_numeric = ['bat_PA', 'pit_IP', 'pit_ER', 'pit_BB', 'pit_H', 'pit_SO']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    team_name_map = {
        '統一獅': '統一7-ELEVEn獅', '統一': '統一7-ELEVEn獅', 'Uni-Lions': '統一7-ELEVEn獅',
        '桃猿': '樂天桃猿', 'Lamigo': '樂天桃猿', 'Rakuten': '樂天桃猿', '樂天': '樂天桃猿',
        '兄弟': '中信兄弟', '兄弟象': '中信兄弟', 'Brothers': '中信兄弟',
        '富邦': '富邦悍將', '悍將': '富邦悍將', '義大': '富邦悍將', '義大犀牛': '富邦悍將',
        '味全': '味全龍', 'Dragons': '味全龍',
        '台鋼': '台鋼雄鷹', 'TSG': '台鋼雄鷹'
    }
    target_teams = ['統一7-ELEVEn獅', '台鋼雄鷹', '中信兄弟', '樂天桃猿', '味全龍', '富邦悍將']

    # 打者資料
    bat_cols = ['Name_clean', 'Team Name_x', 'Year', 'bat_PA', 'bat_AB', 'bat_H', 'bat_HR', 'bat_SB', 'bat_AVG', 'bat_OPS', 'bat_OBP', 'bat_SLG']
    valid_bat_cols = [c for c in bat_cols if c in df.columns]

    df_sorted_bat = df[valid_bat_cols].sort_values(by=['Year', 'bat_PA'], ascending=[False, False])
    df_bat = df_sorted_bat.drop_duplicates(subset=['Name_clean', 'Year'], keep='first')

    df_bat = df_bat.rename(columns={'Name_clean': 'Name', 'Team Name_x': 'Team', 'bat_OPS': 'OPS', 'bat_AVG': 'AVG', 'bat_HR': 'HR', 'bat_SB': 'SB', 'bat_PA': 'PA'})
    df_bat['Team'] = df_bat['Team'].replace(team_name_map)
    df_bat = df_bat[df_bat['Team'].isin(target_teams)]
    df_bat = df_bat[df_bat['PA'] > 0]

    # 投手資料
    df_pit_raw = df[ (df['pit_IP'] > 0) & (df['bat_PA'] < 10) ].copy()

    if 'pit_ER' in df_pit_raw.columns and 'pit_IP' in df_pit_raw.columns:
        df_pit_raw['pit_ERA'] = (df_pit_raw['pit_ER'] * 9) / df_pit_raw['pit_IP'].replace(0, 0.1)
    else:
        df_pit_raw['pit_ERA'] = 0.0

    if 'pit_BB' in df_pit_raw.columns and 'pit_H' in df_pit_raw.columns:
         df_pit_raw['pit_WHIP'] = (df_pit_raw['pit_BB'] + df_pit_raw['pit_H']) / df_pit_raw['pit_IP'].replace(0, 0.1)
    else:
        df_pit_raw['pit_WHIP'] = 0.0

    pit_cols = ['Name_clean', 'Team Name_y', 'Year', 'pit_ERA', 'pit_IP', 'pit_SO', 'pit_BB', 'pit_WHIP']
    valid_pit_cols = [c for c in pit_cols if c in df_pit_raw.columns]

    df_sorted_pit = df_pit_raw[valid_pit_cols].sort_values(by=['Year', 'pit_IP'], ascending=[False, False])
    df_pit = df_sorted_pit.drop_duplicates(subset=['Name_clean', 'Year'], keep='first')

    df_pit = df_pit.rename(columns={'Name_clean': 'Name', 'Team Name_y': 'Team', 'pit_ERA': 'ERA', 'pit_IP': 'IP', 'pit_SO': 'SO', 'pit_BB': 'BB', 'pit_WHIP': 'WHIP'})
    df_pit['Team'] = df_pit['Team'].fillna('Unknown')
    df_pit['Team'] = df_pit['Team'].replace(team_name_map)
    df_pit = df_pit[df_pit['Team'].isin(target_teams)]

    return df_bat, df_pit

df_bat, df_pit = load_data()

# 分頁內容
tab1, tab2, tab3 = st.tabs(["🏆 聯盟戰況", "🏏 打擊排行", "⚾ 投手分析"])

def get_weighted_average(data, value_col, weight_col):
    if data[weight_col].sum() == 0: return 0
    return np.average(data[value_col], weights=data[weight_col])

# Tab 1: 聯盟戰況
with tab1:
    st.subheader("🛠️ 篩選條件")
    all_years = sorted(df_bat['Year'].unique())
    def_year = [2024] if 2024 in all_years else ([max(all_years)] if all_years else [])

    t1_years = st.multiselect("選擇年份 (僅影響下方氣泡圖)", all_years, default=def_year, key="t1_year")

    # 資料篩選
    bat_t1 = df_bat[df_bat['Year'].isin(t1_years)]
    pit_t1 = df_pit[df_pit['Year'].isin(t1_years)]

    st.divider()
    st.header("團隊戰力分析")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 團隊 OPS 年度趨勢")
        team_ops_trend = df_bat.groupby(['Year', 'Team']).apply(
            lambda x: pd.Series({'OPS': get_weighted_average(x, 'OPS', 'PA')})
        ).reset_index()

        if not team_ops_trend.empty:
            fig_trend = px.line(team_ops_trend, x='Year', y='OPS', color='Team', markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.subheader("🛡️ 比較攻守表現：OPS vs ERA")
        team_ops_now = bat_t1.groupby(['Year', 'Team']).apply(
            lambda x: pd.Series({'OPS': get_weighted_average(x, 'OPS', 'PA')})
        ).reset_index()

        if not pit_t1.empty:
            team_era_now = pit_t1.groupby(['Year', 'Team']).apply(
                lambda x: pd.Series({'ERA': get_weighted_average(x, 'ERA', 'IP')})
            ).reset_index()
            team_stats = pd.merge(team_ops_now, team_era_now, on=['Year', 'Team'], how='left')
        else:
            team_stats = team_ops_now

        if 'ERA' in team_stats.columns and not team_stats.empty:
            avg_era = team_stats['ERA'].mean()
            avg_ops = team_stats['OPS'].mean()

            fig_quad = px.scatter(
                team_stats, x='ERA', y='OPS', color='Team',
                text='Year', size=[15]*len(team_stats), hover_name='Team'
            )
            fig_quad.add_vline(x=avg_era, line_dash="dash", line_color="gray", annotation_text="平均ERA")
            fig_quad.add_hline(y=avg_ops, line_dash="dash", line_color="gray", annotation_text="平均OPS")
            fig_quad.update_layout(xaxis=dict(autorange="reversed"))

            if len(t1_years) == 1:
                fig_quad.update_layout(title=f"{t1_years[0]} 年賽季戰力分佈")

            st.plotly_chart(fig_quad, use_container_width=True)
        else:
            st.info("請選擇年份以顯示資料")

# Tab 2: 打擊排行
with tab2:
    st.header("打擊數據排行榜")

    max_pa_val = int(df_bat['PA'].max()) if not df_bat.empty else 100
    min_pa = st.slider("最少打席數 (PA)", 0, max_pa_val, 50, key="t2_slider")

    bat_display = df_bat[df_bat['PA'] >= min_pa].sort_values('OPS', ascending=False)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("💥 強打者分佈 (PA vs OPS)")
        fig = px.scatter(bat_display, x='PA', y='OPS', color='Team', hover_name='Name', size='HR')
        if not bat_display.empty:
            fig.add_hline(y=bat_display['OPS'].mean(), line_dash="dash", annotation_text="平均")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 排行榜")
        st.dataframe(
            bat_display[['Name', 'Team', 'OPS', 'AVG', 'HR', 'SB', 'Year']],
            column_config={
                "OPS": st.column_config.ProgressColumn("OPS", min_value=0, max_value=1.5, format="%.3f"),
                "AVG": st.column_config.NumberColumn("AVG", format="%.3f"),
                "Year": st.column_config.NumberColumn("年份", format="%d")
            },
            height=500,
            hide_index=True
        )

# Tab 3: 投手分析
with tab3:
    st.subheader("🛠️ 篩選條件")

    t3_teams = st.multiselect("選擇球隊", df_pit['Team'].unique(), default=df_pit['Team'].unique(), key="t3_team")
    pit_t3 = df_pit[df_pit['Team'].isin(t3_teams)]

    st.divider()
    st.header("投手進階數據")

    if pit_t3.empty:
        st.warning("⚠️ 篩選條件下無投手資料")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🎯 三振 (SO) vs 防禦率 (ERA)")
            fig = px.scatter(pit_t3, x='SO', y='ERA', color='Team', hover_name='Name', size='IP')
            fig.update_layout(yaxis=dict(range=[10, 0], title="ERA (防禦率)"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🕸️ 投手能力雷達圖")
            df_radar = pit_t3[['Name', 'ERA', 'WHIP', 'SO', 'BB', 'IP']].copy()

            target = st.selectbox("選擇投手", df_radar['Name'].unique(), key="t3_select")

            if target:
                metrics = {'ERA': False, 'WHIP': False, 'SO': True, 'BB': False, 'IP': True}
                for col, higher_is_better in metrics.items():
                    min_val = df_radar[col].min()
                    max_val = df_radar[col].max()
                    if max_val == min_val:
                        df_radar[f'{col}_Score'] = 50
                    else:
                        if higher_is_better:
                            df_radar[f'{col}_Score'] = (df_radar[col] - min_val) / (max_val - min_val) * 100
                        else:
                            df_radar[f'{col}_Score'] = (max_val - df_radar[col]) / (max_val - min_val) * 100

                p_data = df_radar[df_radar['Name'] == target].iloc[0]
                avg_score = df_radar[[f'{k}_Score' for k in metrics.keys()]].mean()
                categories = list(metrics.keys())
                player_scores = [p_data[f'{c}_Score'] for c in categories]
                league_avg_scores = [avg_score[f'{c}_Score'] for c in categories]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=player_scores, theta=categories, fill='toself', name=p_data['Name'], line_color='blue'))
                fig.add_trace(go.Scatterpolar(r=league_avg_scores, theta=categories, fill='toself', name='聯盟平均', line_color='gray', opacity=0.5))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title=f"能力值評分 (0-100)")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("註：圖表顯示的是「PR評分」(0~100)，越外圈代表該項能力在聯盟中越強。")
