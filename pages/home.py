import streamlit as st
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent

st.markdown("""
<style>
[data-testid="stPageLink"] a,
[data-testid="stPageLink"] a * {
    background-color: #4D4D4D !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
    border-radius: 6px;
    text-decoration: none;
}
[data-testid="stPageLink"] a:hover,
[data-testid="stPageLink"] a:hover * {
    background-color: #333333 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("PMC智能助手")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("📦 MRB 看板")
        st.caption("MRB 库存趋势 · 库龄分析 · 缺料跟踪")
        c1, c2 = st.columns(2)
        with c1:
            try:
                df_stock = pd.read_excel(BASE / "MRB库存.xlsx", sheet_name="MRB总表")
                st.metric("MRB 库存物料数", len(df_stock))
            except Exception:
                st.metric("MRB 库存物料数", "—")
        with c2:
            try:
                df_short = pd.read_excel(BASE / "MRB缺料.xlsx", sheet_name="待开工缺料")
                st.metric("缺料物料数", len(df_short))
            except Exception:
                st.metric("缺料物料数", "—")
        st.page_link("pages/mrb.py", label="进入看板 →", use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("⚠️ 待开工单缺料看板")
        st.caption("生产备料单最终缺料明细 · 含各工单分解 · 交期跟踪")
        c1, c2 = st.columns(2)
        with c1:
            try:
                df_prod = pd.read_excel(BASE / "待开工缺料详情.xlsx", sheet_name=0)
                st.metric("缺料物料数", len(df_prod))
            except Exception:
                st.metric("缺料物料数", "—")
        with c2:
            st.metric("数据来源", "生产备料单")
        st.page_link("pages/shortage.py", label="进入看板 →", use_container_width=True)
