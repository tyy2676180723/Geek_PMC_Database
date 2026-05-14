import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="MRB 看板", layout="wide")
st.title("MRB 看板")

BASE = Path(__file__).parent.parent

tab1, tab2, tab3 = st.tabs(["📈 趋势图", "📦 MRB库存", "⚠️ MRB缺料"])

with tab1:
    img_path = BASE / "mrb_trend.png"
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.warning("未找到 mrb_trend.png")

with tab2:
    xls_path = BASE / "MRB库存.xlsx"
    if xls_path.exists():
        xls = pd.ExcelFile(xls_path)
        sub1, sub2, sub3 = st.tabs(xls.sheet_names)
        sheets = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
        with sub1:
            st.dataframe(sheets[xls.sheet_names[0]], use_container_width=True)
        with sub2:
            st.dataframe(sheets[xls.sheet_names[1]], use_container_width=True)
        with sub3:
            st.dataframe(sheets[xls.sheet_names[2]], use_container_width=True)
    else:
        st.warning("未找到 MRB库存.xlsx")

with tab3:
    xls_path2 = BASE / "MRB缺料.xlsx"
    if xls_path2.exists():
        xls2 = pd.ExcelFile(xls_path2)
        sub_a, sub_b = st.tabs(xls2.sheet_names)
        sheets2 = {name: pd.read_excel(xls2, sheet_name=name) for name in xls2.sheet_names}
        with sub_a:
            df = sheets2[xls2.sheet_names[0]]
            st.metric("缺料物料数", len(df))
            st.dataframe(df, use_container_width=True)
        with sub_b:
            df2 = sheets2[xls2.sheet_names[1]]
            st.metric("待开工缺料数", len(df2))
            st.dataframe(df2, use_container_width=True)
    else:
        st.warning("未找到 MRB缺料.xlsx")
