import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import joblib
from sklearn.preprocessing import StandardScaler
from shared.styles import apply_global_style

MODEL_PATH = "cpbl_ai_model.pkl"
META_PATH = "cpbl_meta_learner.pkl"
SCALER_PATH = "scaler.pkl"
BAT_DATA_PATH = "player_features_for_app.csv"
PIT_DATA_PATH = "pitcher_stats_for_app.csv"

PARK_FACTORS = {
    "洲際": {"Runs": 1.19}, "澄清湖": {"Runs": 1.03}, "天母": {"Runs": 0.96},
    "新莊": {"Runs": 0.90}, "樂天桃園": {"Runs": 1.18}, "台南": {"Runs": 0.91},
    "台北大巨蛋": {"Runs": 0.84}
}

STADIUM_MAP = {
    "統一7-ELEVEn獅": ["台南"], "中信兄弟": ["洲際"], "樂天桃猿": ["樂天桃園"],
    "味全龍": ["天母", "台北大巨蛋"], "富邦悍將": ["新莊"], "台鋼雄鷹": ["澄清湖"]
}

TEAM_ROSTERS = {
    "統一7-ELEVEn獅": {
        "pitchers": ["陳韻文", "蒙德茲", "劉予承", "髙塩將樹", "鍾允華", "邱浩鈞", "王鏡銘", "獅帝芬", "吳承諭", "胡智爲", "李軍", "辛俊昇", "郭俊麟", "飛力獅"],
        "batters": ["陳傑憲", "林安可", "蘇智傑", "陳鏞基", "潘傑楷", "邱智呈", "陳聖平", "陳重羽", "林佳緯", "胡金龍", "林子豪", "許哲晏", "陳重廷", "林泓弦", "林祖傑", "林岱安", "柯育民", "朱迦恩"]
    },
    "台鋼雄鷹": {
        "pitchers": ["江承諺", "陳柏清", "艾速特", "黃群", "王躍霖", "林詩翔", "韋宏亮", "黃紹睿", "櫻井周斗", "許育銘", "張誠恩", "郭俞延"],
        "batters": ["魔鷹", "曾子祐", "王柏融", "吳念庭", "王博玄", "杜家明", "郭阜林", "郭永維", "葉保弟", "陳文杰", "藍寅倫", "紀慶然", "顏郁軒", "林家鋐", "曾昱磬", "高聖恩", "陳致嘉", "陳世嘉"]
    },
    "中信兄弟": {
        "pitchers": ["德保拉", "呂彥青", "吳俊偉", "蔡齊哲", "李振昌", "鄭凱文", "魏碩成", "林暉盛", "江忠城", "羅戈", "鄭浩均", "李博登", "盧孟揚", "伍立辰", "韋禮加"],
        "batters": ["江坤宇", "王威晨", "許基宏", "陳俊秀", "岳政華", "曾頌恩", "詹子賢", "岳東華", "高宇杰", "張志豪", "王政順", "林志綱", "張仁瑋", "黃韋盛", "許庭綸", "宋晟睿", "陳統恩", "徐博瑋"]
    },
    "樂天桃猿": {
        "pitchers": ["威能帝", "魔神樂", "黃子鵬", "陳冠宇", "陳柏豪", "蘇俊璋", "莊昕諺", "王志煊", "賴胤豪", "朱承洋", "凱樂", "邱駿威", "林子崴", "陳克羿"],
        "batters": ["林立", "梁家榮", "廖健富", "陳晨威", "林承飛", "朱育賢", "林泓育", "馬傑森", "林子偉", "林智平", "成晉", "余德龍", "林政華", "何品室融", "鍾玉成", "許賀捷", "李勛傑", "宋嘉翔", "張閔勛", "嚴宏鈞"]
    },
    "味全龍": {
        "pitchers": ["徐若熙", "鋼龍", "陳冠偉", "林凱威", "林子昱", "郭郁政", "陳禹勳", "曹祐齊", "張景淯", "呂偉晟", "李致霖", "趙璟榮", "陳志杰", "張鈞守", "黃暐傑", "林鋅杰"],
        "batters": ["吉力吉撈．鞏冠", "李凱威", "劉基鴻", "郭天信", "張政禹", "蔣少宏", "拿莫．伊漾", "林孝程", "劉俊緯", "陳思仲", "周委宏", "瑪仕革斯．俄霸律尼", "朱育賢", "王順和", "張祐銘", "張祐嘉", "林辰勳"]
    },
    "富邦悍將": {
        "pitchers": ["曾峻岳", "王尉永", "江國豪", "黃保羅", "賴鴻誠", "廖任磊", "范柏絜", "李吳永勤", "魔力藍", "力亞士", "游霆崴", "林栚呈"],
        "batters": ["張育成", "申皓瑋", "范國宸", "戴培峰", "王正棠", "董子恩", "王念好", "池恩齊", "李宗賢", "林澤彬", "高捷", "葉子霆", "黃兆維", "林岳谷", "潘瑋祥", "陳真", "張洺瑀", "蔡佳諺", "周佳樂", "豊暐", "魏全"]
    }
}

@st.cache_resource
@st.cache_resource
def load_all_resources():
    files = [MODEL_PATH, META_PATH, SCALER_PATH, BAT_DATA_PATH, PIT_DATA_PATH]
    for f in files:
        if not os.path.exists(f):
            st.error(f"找不到檔案: {f}")
            st.stop()
    
    m = joblib.load(MODEL_PATH)
    me = joblib.load(META_PATH)
    sc = joblib.load(SCALER_PATH)
    df_b = pd.read_csv(BAT_DATA_PATH)
    df_p = pd.read_csv(PIT_DATA_PATH)
    
    df_b.columns = df_b.columns.str.strip()
    df_p.columns = df_p.columns.str.strip()
    
    return m, me, sc, df_b, df_p

model, meta_model, scaler, df_bat, df_pit = load_all_resources()

first_est = model.estimators_[0]
current_order = first_est.feature_names_ if hasattr(first_est, 'feature_names_') else first_est.feature_names_in_

apply_global_style()
st.header("🔮 2026 棒球比賽預測系統")

col_h, col_vs, col_a = st.columns([1, 0.2, 1])
with col_h:
    st.subheader("🏠 主隊 (Home)")
    h_team = st.selectbox("選擇主隊", list(STADIUM_MAP.keys()), key="h_t")
    h_stadium = st.selectbox("🏟️ 比賽球場", STADIUM_MAP[h_team], key="h_st")
    h_sp = st.selectbox("⚾ 選擇先發投手", TEAM_ROSTERS[h_team]["pitchers"], key="h_p")
    h_lineup = st.multiselect("📋 選擇打線 (9人)", TEAM_ROSTERS[h_team]["batters"], key="h_l")

with col_a:
    st.subheader("✈️ 客隊 (Away)")
    a_team = st.selectbox("選擇客隊", [t for t in STADIUM_MAP.keys() if t != h_team], key="a_t")
    a_sp = st.selectbox("選擇先發投手", TEAM_ROSTERS[a_team]["pitchers"], key="a_p")
    a_lineup = st.multiselect("選擇打線 (9人)", TEAM_ROSTERS[a_team]["batters"], key="a_l")

if st.button("🚀 執行預測", use_container_width=True):
    if len(h_lineup) != 9 or len(a_lineup) != 9:
        st.warning("⚠️ 請確保兩隊皆選滿 9 位打者。")
    else:
        with st.spinner("正在解析..."):

            def get_team_wraa(names, expected_order):
                wraa_total = 0
                found_names = []
                for name in names:
                    hist = df_bat[
                        (df_bat['Name_Display'].str.strip() == name.strip()) &
                        (df_bat['Year_Display'].isin([2024, 2025]))
                    ].sort_values('Year_Display', ascending=False)

                    if not hist.empty:
                        found_names.append(name)
                        weights = [0.7, 0.3]
                        vals = []
                        for i in range(min(2, len(hist))):
                            row = hist.iloc[[i]]
                            feat_raw = row.drop(columns=['Name_Display','Team_Display','Year_Display','Real_OPS'], errors='ignore')
                            feat_aligned = feat_raw.reindex(columns=expected_order, fill_value=0)
                            feat_aligned = feat_aligned.apply(pd.to_numeric, errors='coerce').fillna(0)
                            vals.append(model.predict(feat_aligned)[0])

                        w_use = weights[:len(vals)]
                        if sum(w_use) > 0:
                            w_norm = [w/sum(w_use) for w in w_use]
                            wraa_total += np.average(vals, weights=w_norm)
                return wraa_total, found_names

            # 計算打擊與投手數據
            h_wraa, h_found = get_team_wraa(h_lineup, current_order)
            a_wraa, a_found = get_team_wraa(a_lineup, current_order)

            def get_fip(name):
                name_col = 'Name' if 'Name' in df_pit.columns else 'Name_Display'
                res = df_pit[df_pit[name_col].str.strip() == name.strip()].sort_values('Year', ascending=False)['FIP']
                return res.values[0] if not res.empty else 4.2

            h_fip, a_fip = get_fip(h_sp), get_fip(a_sp)
            pf_val = PARK_FACTORS[h_stadium]["Runs"]

            # 預測計算
            wraa_diff = h_wraa - a_wraa
            fip_diff = a_fip - h_fip

            X_raw = np.array([[wraa_diff, fip_diff, pf_val]])
            X_scaled = scaler.transform(X_raw)
            win_prob_raw = meta_model.predict_proba(X_scaled)[0][1]

            # 邏輯修正
            adjustment = 0.33
            logit_raw = np.log(win_prob_raw / (1 - win_prob_raw))
            logit_final = logit_raw + adjustment
            win_prob = 1 / (1 + np.exp(-logit_final))
            win_prob = np.clip(win_prob, 0.05, 0.95)

            # 診斷面板
            with st.expander("🔍 數據診斷與計算過程"):
                st.markdown("### 1. 打擊戰力 (wRAA)")
                st.write(f"- 主隊總預估 wRAA: `{h_wraa:.2f}`")
                st.write(f"- 客隊總預估 wRAA: `{a_wraa:.2f}`")
                st.info(f"💡 **打擊差距 (wraa_diff)** = `{wraa_diff:.2f}`")

                st.markdown("---")
                st.markdown("### 2. 投手壓制力 (FIP)")
                st.write(f"- 主隊先發 ({h_sp}) FIP: `{h_fip:.2f}`")
                st.write(f"- 客隊先發 ({a_sp}) FIP: `{a_fip:.2f}`")
                st.info(f"💡 **投手差距 (fip_diff)** = `{fip_diff:.2f}`")

                st.markdown("---")
                st.markdown("### 3. 最終推論與修正")
                st.write(f"- 球場因子 (PF): `{pf_val:.2f}`")
                st.write(f"- 模型原始預測: `{win_prob_raw*100:.2f}%`")

                st.latex(r"Logit_{raw} = \ln\left(\frac{P_{raw}}{1-P_{raw}}\right) = " + f"{logit_raw:.3f}")
                st.write(f"- 主場修正強度: `+{adjustment}`")
                st.latex(r"Prob_{final} = \frac{1}{1 + e^{-(Logit_{raw} + " + str(adjustment) + ")}}")

                st.success(f"修正後最終勝率: **{win_prob*100:.2f}%**")

            # 圖表
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = win_prob * 100,
                title = {'text': f"{h_team} 勝率預估 (%)"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#002D62"},
                    'steps': [
                        {'range': [0, 45], 'color': "#FFCCCC"},
                        {'range': [45, 55], 'color': "#EEEEEE"},
                        {'range': [55, 100], 'color': "#CCFFCC"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

            if win_prob > 0.55: st.success(f"**AI 評論**：{h_team} 在 {h_stadium} 具有明顯優勢。")
            elif win_prob < 0.45: st.error(f"**AI 評論**：客隊 {a_team} 的戰力預期較為強勢。")
            else: st.info("**AI 評論**：雙方戰力平衡，主場因素將是勝負關鍵。")
