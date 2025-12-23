import time
from io import BytesIO

import requests
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="小互動", page_icon="👾", layout="wide")

BASE_URL = "https://raw.githubusercontent.com/ChewyChloe/cpbl-project/main/game"

ASSET_VER = "2025-12-24-1"

def v(url: str) -> str:
    return f"{url}?v={ASSET_VER}"

IMAGES = {
    "BG": v(f"{BASE_URL}/playground.png"),
    "P": v(f"{BASE_URL}/P.png"),
    "C": v(f"{BASE_URL}/C.png"),
    "1B": v(f"{BASE_URL}/1B.png"),
    "2B": v(f"{BASE_URL}/2B.png"),
    "3B": v(f"{BASE_URL}/3B.png"),
    "SS": v(f"{BASE_URL}/SS.png"),
    "LF": v(f"{BASE_URL}/LF.png"),
    "CF": v(f"{BASE_URL}/CF.png"),
    "RF": v(f"{BASE_URL}/RF.png"),
    "Batter": v(f"{BASE_URL}/batter.png"),
}

players_data = {
    "P": {"name": "王牌投手", "desc": "我是球場上的獨裁者，掌控比賽節奏！"},
    "C": {"name": "鐵壁捕手", "desc": "我是場上的指揮官，想得分先過我這關！"},
    "1B": {"name": "一壘大砲", "desc": "不管是接球還是打擊，我都是最穩定的存在。"},
    "2B": {"name": "靈活二壘", "desc": "雙殺守備是我的拿手好戲，誰都別想穿越中線！"},
    "3B": {"name": "熱角三壘", "desc": "強襲球來吧！我的反應神經可是全隊最快的。"},
    "SS": {"name": "遊擊手", "desc": "內野防守核心，守備範圍無極限！"},
    "LF": {"name": "左外野手", "desc": "這球飛得好遠...但我一定接得到！"},
    "CF": {"name": "中外野手", "desc": "我是外野的隊長，這片草地由我守護。"},
    "RF": {"name": "右外野手", "desc": "想跑三壘？小心我的長傳狙擊！"},
    "Batter": {"name": "打擊者", "desc": "我的工作只有一個：把那顆小白球轟出場外！"},
}

FIELD_W = 800
FIELD_H = 600

# 位置
PLACEMENTS = {
    "P": {"top": 0.57, "left": 0.40, "w": 135, "h": 135},
    "C": {"top": 0.80, "left": 0.42, "w": 120, "h": 120},
    "Batter": {"top": 0.70, "left": 0.37, "w": 135, "h": 135},
    "1B": {"top": 0.55, "left": 0.63, "w": 135, "h": 135},
    "2B": {"top": 0.38, "left": 0.52, "w": 110, "h": 110},
    "3B": {"top": 0.58, "left": 0.22, "w": 135, "h": 135},
    "SS": {"top": 0.40, "left": 0.32, "w": 80, "h": 80},
    "LF": {"top": 0.28, "left": 0.15, "w": 135, "h": 135},
    "CF": {"top": 0.18, "left": 0.40, "w": 135, "h": 135},
    "RF": {"top": 0.32, "left": 0.70, "w": 135, "h": 135},
}

# 對話框）
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.stApp {
    font-family: 'Courier New', monospace;
    background-color: #202020;
}

.rpg-box-container {
    background-color: #000080;
    border: 6px solid #ffffff;
    padding: 5px;
    box-shadow: 5px 5px 0px #000000;
    margin-top: 16px;
}
.rpg-box-inner {
    background-color: #000080;
    border: 4px solid #000080;
    padding: 18px;
    color: white;
    font-family: 'Press Start 2P', cursive !important;
    line-height: 1.8;
    font-size: 16px;
    min-height: 120px;
}
.char-name-tag {
    font-family: 'Press Start 2P', cursive !important;
    background-color: #e0c050;
    color: #000000;
    padding: 5px 15px;
    border: 3px solid #ffffff;
    display: inline-block;
    margin-bottom: -10px;
    margin-left: 10px;
    box-shadow: 3px 3px 0px #000000;
}
</style>
""", unsafe_allow_html=True)

# 點擊判定
@st.cache_data(show_spinner=False)
def fetch_image(url: str, ver: str) -> Image.Image:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGBA")

def build_map(selected_role: str | None):
    bg = fetch_image(IMAGES["BG"], ASSET_VER).resize((FIELD_W, FIELD_H))
    regions = {}

    for role, p in PLACEMENTS.items():
        scale = 1.3 if role == selected_role else 1.0
        w = int(p["w"] * scale)
        h = int(p["h"] * scale)

        sprite = fetch_image(IMAGES[role], ASSET_VER).resize((w, h))

        x = int(p["left"] * FIELD_W)
        y = int(p["top"] * FIELD_H)

        bg.alpha_composite(sprite, (x, y))
        regions[role] = (x, y, x + w, y + h)

    return bg, regions

def detect_role(x: int, y: int, regions: dict) -> str | None:
    for role, (x1, y1, x2, y2) in regions.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return role
    return None

# 狀態
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "last_click" not in st.session_state:
    st.session_state.last_click = None
if "last_typed_role" not in st.session_state:
    st.session_state.last_typed_role = None

st.title("👾 像素棒球場")

left, right = st.columns([2.2, 1.0], vertical_alignment="top")

with left:
    field_img, regions = build_map(st.session_state.selected_role)
    clicked = streamlit_image_coordinates(field_img, width=FIELD_W)

    if clicked and "x" in clicked and "y" in clicked:
        xy = (int(clicked["x"]), int(clicked["y"]))
        if xy != st.session_state.last_click:
            st.session_state.last_click = xy
            st.session_state.selected_role = detect_role(xy[0], xy[1], regions)
            if st.session_state.selected_role != st.session_state.last_typed_role:
                st.session_state.last_typed_role = None

with right:
    role = st.session_state.selected_role

    if role:
        data = players_data[role]

        st.image(IMAGES[role], width=180)

        st.markdown(f'<div class="char-name-tag">{data["name"]}</div>', unsafe_allow_html=True)
        box = st.empty()

        if st.session_state.last_typed_role != role:
            st.session_state.last_typed_role = role
            text = ""
            for ch in data["desc"]:
                text += ch
                box.markdown(f"""
                <div class="rpg-box-container">
                    <div class="rpg-box-inner">{text}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.04)
        else:
            box.markdown(f"""
            <div class="rpg-box-container">
                <div class="rpg-box-inner">{data["desc"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="rpg-box-container">
            <div class="rpg-box-inner">
                （點擊球場上的球員，他們就會回應你。）
            </div>
        </div>
        """, unsafe_allow_html=True)
