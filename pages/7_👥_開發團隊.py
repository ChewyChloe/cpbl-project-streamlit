import streamlit as st
from shared.styles import apply_global_style

apply_global_style()
def apply_global_style():
    st.markdown(custom_css, unsafe_allow_html=True)
st.header("👥 開發團隊")
st.markdown("---")

team_members = [{"id": "113403001", "dept": "資管二", "name": "呂沛珍"}]

cols = st.columns(4)
for i, member in enumerate(team_members):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="team-card">
            <div class="team-name">{member['name']}</div>
            <div class="team-info">{member['dept']}</div>
            <div class="team-info">{member['id']}</div>
        </div>
        """, unsafe_allow_html=True)
