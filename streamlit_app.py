import streamlit as st

st.set_page_config(page_title="PMC智能助手", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { min-width: 300px; max-width: 300px; }
</style>
""", unsafe_allow_html=True)

home = st.Page("pages/home.py", title="主页", icon="🏠", default=True)
mrb = st.Page("pages/mrb.py", title="MRB 看板", icon="📦")
shortage = st.Page("pages/shortage.py", title="待开工单缺料看板", icon="⚠️")

pg = st.navigation([home, mrb, shortage])
pg.run()
