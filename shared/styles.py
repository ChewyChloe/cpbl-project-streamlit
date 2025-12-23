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
