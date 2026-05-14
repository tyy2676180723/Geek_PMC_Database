import re
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

ASSEMBLY_RE = re.compile(r'^\d{2}\.\d{2}\.\d{5}$')
assembly_cols = [c for c in df.columns if ASSEMBLY_RE.match(str(c))]
normal_cols   = [c for c in df.columns if not ASSEMBLY_RE.match(str(c))]

# ── 顶部指标 ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("缺料物料数", len(df))
with m2:
    total = df["最终缺料"].sum() if "最终缺料" in df.columns else 0
    st.metric("缺料总数量", f"{total:,.0f}")
with m3:
    st.metric("涉及供应商数", df["供应商"].nunique() if "供应商" in df.columns else "—")
with m4:
    st.metric("涉及采购员数", df["采购"].nunique() if "采购" in df.columns else "—")

st.markdown("---")

# ── 动态筛选 ──────────────────────────────────────────────────────────────────
COLS_PER_ROW  = 4
MULTISEL_MAX  = 50   # 唯一值超过此数改用关键字搜索

with st.expander("筛选条件", expanded=True):
    df_view = df.copy()

    # 1. 成品料号筛选（所有 ##.##.##### 列合并为一个多选）
    if assembly_cols:
        st.markdown("**成品料号**")
        sel_asm = st.multiselect(
            "成品料号",
            options=assembly_cols,
            default=[],
            label_visibility="collapsed",
            key="f_assembly"
        )
        if sel_asm:
            mask = pd.Series(False, index=df_view.index)
            for c in sel_asm:
                mask |= (df_view[c].notna() & (df_view[c] != 0))
            df_view = df_view[mask]
        st.markdown("---")

    # 2. 其余列：多选 or 关键字搜索（无滑块）
    for row_start in range(0, len(normal_cols), COLS_PER_ROW):
        row_cols = normal_cols[row_start: row_start + COLS_PER_ROW]
        ui_cols  = st.columns(len(row_cols))
        for ui_col, col in zip(ui_cols, row_cols):
            with ui_col:
                series  = df[col].dropna()
                n_uniq  = series.nunique()
                if n_uniq <= MULTISEL_MAX:
                    options = sorted(series.unique().tolist(), key=str)
                    sel = st.multiselect(col, options, default=options, key=f"f_{col}")
                    if len(sel) < len(options):
                        df_view = df_view[df_view[col].isin(sel) | df_view[col].isna()]
                else:
                    kw = st.text_input(col, placeholder="关键字搜索", key=f"f_{col}")
                    if kw:
                        df_view = df_view[
                            df_view[col].astype(str).str.contains(kw, case=False, na=False)
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
