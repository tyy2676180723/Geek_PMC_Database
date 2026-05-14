import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="待开工单缺料看板", layout="wide")
st.title("待开工单缺料看板")

BASE = Path(__file__).parent.parent
data_path = BASE / "待开工缺料详情.xlsx"

if not data_path.exists():
    st.warning("暂无数据，请先运行机器人核料脚本生成数据。")
    st.stop()

df = pd.read_excel(data_path, sheet_name=0)

# ── 顶部指标 ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("缺料物料数", len(df))
with col2:
    total_shortage = df["最终缺料"].sum() if "最终缺料" in df.columns else 0
    st.metric("缺料总数量", f"{total_shortage:,.0f}")
with col3:
    suppliers = df["供应商"].nunique() if "供应商" in df.columns else 0
    st.metric("涉及供应商数", suppliers)
with col4:
    buyers = df["采购"].nunique() if "采购" in df.columns else 0
    st.metric("涉及采购员数", buyers)

st.markdown("---")

# ── 筛选栏 ────────────────────────────────────────────────────────────────────
with st.expander("筛选条件", expanded=False):
    fc1, fc2 = st.columns(2)
    with fc1:
        if "供应商" in df.columns:
            suppliers_list = ["全部"] + sorted(df["供应商"].dropna().unique().tolist())
            sel_supplier = st.selectbox("供应商", suppliers_list)
        else:
            sel_supplier = "全部"
    with fc2:
        if "采购" in df.columns:
            buyers_list = ["全部"] + sorted(df["采购"].dropna().unique().tolist())
            sel_buyer = st.selectbox("采购员", buyers_list)
        else:
            sel_buyer = "全部"

df_view = df.copy()
if sel_supplier != "全部":
    df_view = df_view[df_view["供应商"] == sel_supplier]
if sel_buyer != "全部":
    df_view = df_view[df_view["采购"] == sel_buyer]

# ── 主表格 ────────────────────────────────────────────────────────────────────
CORE_COLS = ["序号", "子项物料编码", "子项物料名称", "子项物料规格",
             "应发数量", "工单欠料", "即时库存", "收料", "最终缺料",
             "交期", "供应商", "采购"]
core_cols_exist = [c for c in CORE_COLS if c in df_view.columns]

tab1, tab2 = st.tabs(["核心字段", "完整数据（含工单分解）"])

with tab1:
    st.dataframe(
        df_view[core_cols_exist].style.highlight_between(
            subset=["最终缺料"] if "最终缺料" in core_cols_exist else [],
            left=-9999, right=-0.01, color="#FFCCCC"
        ),
        use_container_width=True,
        height=500,
    )

with tab2:
    st.dataframe(df_view, use_container_width=True, height=500)
