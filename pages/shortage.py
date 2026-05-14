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

# ── 动态筛选：所有列 ──────────────────────────────────────────────────────────
CATEGORICAL_MAX = 30   # 唯一值 ≤ 此数视为分类列，用 multiselect

with st.expander("筛选条件", expanded=True):
    df_view = df.copy()
    cols = list(df.columns)
    # 每行放 4 个筛选控件
    COLS_PER_ROW = 4
    for row_start in range(0, len(cols), COLS_PER_ROW):
        row_cols = cols[row_start: row_start + COLS_PER_ROW]
        ui_cols = st.columns(len(row_cols))
        for ui_col, col in zip(ui_cols, row_cols):
            with ui_col:
                series = df[col].dropna()
                # 数值列 → 范围滑块
                if pd.api.types.is_numeric_dtype(df[col]) and series.nunique() > 2:
                    mn, mx = float(series.min()), float(series.max())
                    if mn < mx:
                        sel = st.slider(col, mn, mx, (mn, mx), key=f"f_{col}")
                        df_view = df_view[
                            (df_view[col].isna()) |
                            ((df_view[col] >= sel[0]) & (df_view[col] <= sel[1]))
                        ]
                # 分类列（唯一值少）→ multiselect
                elif series.nunique() <= CATEGORICAL_MAX:
                    options = sorted(series.unique().tolist(), key=str)
                    sel = st.multiselect(col, options, default=options, key=f"f_{col}")
                    if sel:
                        df_view = df_view[df_view[col].isin(sel) | df_view[col].isna()]
                # 文本列（唯一值多）→ 关键字搜索
                else:
                    keyword = st.text_input(col, placeholder="关键字搜索", key=f"f_{col}")
                    if keyword:
                        df_view = df_view[
                            df_view[col].astype(str).str.contains(keyword, case=False, na=False)
                        ]

st.caption(f"筛选后：{len(df_view)} / {len(df)} 条")

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
