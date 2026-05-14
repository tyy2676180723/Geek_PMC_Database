import streamlit as st
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="生产数据看板", layout="wide")

st.title("生产数据看板")
st.markdown("---")

BASE = Path(__file__).parent

def card_metric(path, label):
    """读取文件，返回简单摘要文字"""
    try:
        if not path.exists():
            return "数据待更新"
        if path.suffix == ".xlsx":
            df = pd.read_excel(path, sheet_name=0)
            return f"共 {len(df)} 条记录"
        return "已就绪"
    except Exception:
        return "数据待更新"

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("📦 MRB 看板")
        st.caption("MRB 库存趋势 · 库龄分析 · 缺料跟踪")
        c1, c2 = st.columns(2)
        with c1:
            df_stock = None
            try:
                df_stock = pd.read_excel(BASE / "MRB库存.xlsx", sheet_name="MRB总表")
            except Exception:
                pass
            st.metric("MRB 库存物料数", len(df_stock) if df_stock is not None else "—")
        with c2:
            df_short = None
            try:
                df_short = pd.read_excel(BASE / "MRB缺料.xlsx", sheet_name="待开工缺料")
            except Exception:
                pass
            st.metric("缺料物料数", len(df_short) if df_short is not None else "—")
        st.page_link("pages/1_MRB看板.py", label="进入看板 →", use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("⚠️ 待开工单缺料看板")
        st.caption("生产备料单最终缺料明细 · 含各工单分解 · 交期跟踪")
        c1, c2 = st.columns(2)
        with c1:
            df_prod = None
            try:
                df_prod = pd.read_excel(BASE / "待开工缺料详情.xlsx", sheet_name=0)
            except Exception:
                pass
            st.metric("缺料物料数", len(df_prod) if df_prod is not None else "—")
        with c2:
            st.metric("数据来源", "生产备料单")
        st.page_link("pages/2_待开工单缺料看板.py", label="进入看板 →", use_container_width=True)
