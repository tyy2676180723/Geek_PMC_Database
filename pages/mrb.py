import json
import subprocess
from datetime import date

import streamlit as st
import pandas as pd
from pathlib import Path
from utils import show_table, editable_table

st.title("MRB 看板")

BASE = Path(__file__).parent.parent
PROGRESS_FILE = BASE / "mrb_progress.json"


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"工单缺料": {}, "待开工缺料": {}}


def save_progress(prog: dict):
    PROGRESS_FILE.write_text(
        json.dumps(prog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    subprocess.run(["git", "add", "mrb_progress.json"], cwd=str(BASE), capture_output=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(BASE), capture_output=True)
    if diff.returncode != 0:
        today = date.today().strftime("%Y-%m-%d")
        subprocess.run(["git", "commit", "-m", f"MRB处理进度更新 {today}"], cwd=str(BASE), capture_output=True)
        subprocess.run(["git", "push"], cwd=str(BASE), capture_output=True)


def merge_progress(df: pd.DataFrame, sheet_name: str, prog: dict):
    key_col = "物料编码" if "物料编码" in df.columns else df.columns[0]
    mapping = prog.get(sheet_name, {})
    df = df.copy()
    df["处理进度"] = df[key_col].astype(str).map(mapping).fillna("")
    return df, key_col


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
            show_table(sheets[xls.sheet_names[0]], key="mrb_stock_0")
        with sub2:
            show_table(sheets[xls.sheet_names[1]], key="mrb_stock_1")
        with sub3:
            show_table(sheets[xls.sheet_names[2]], key="mrb_stock_2")
    else:
        st.warning("未找到 MRB库存.xlsx")

with tab3:
    xls_path2 = BASE / "MRB缺料.xlsx"
    if xls_path2.exists():
        prog = load_progress()
        xls2 = pd.ExcelFile(xls_path2)
        sheets2 = {name: pd.read_excel(xls2, sheet_name=name) for name in xls2.sheet_names}
        sub_a, sub_b = st.tabs(xls2.sheet_names)

        with sub_a:
            sname = xls2.sheet_names[0]
            df_a, key_a = merge_progress(sheets2[sname], sname, prog)
            st.metric("缺料物料数", len(df_a))
            edited_a = editable_table(df_a, ["处理进度"], key="shortage_a")
            if st.button("💾 保存处理进度", key="save_a", type="primary"):
                prog[sname] = dict(zip(edited_a[key_a].astype(str), edited_a["处理进度"]))
                save_progress(prog)
                st.success("已保存并推送")

        with sub_b:
            sname2 = xls2.sheet_names[1]
            df_b, key_b = merge_progress(sheets2[sname2], sname2, prog)
            st.metric("待开工缺料数", len(df_b))
            edited_b = editable_table(df_b, ["处理进度"], key="shortage_b")
            if st.button("💾 保存处理进度", key="save_b", type="primary"):
                prog[sname2] = dict(zip(edited_b[key_b].astype(str), edited_b["处理进度"]))
                save_progress(prog)
                st.success("已保存并推送")
    else:
        st.warning("未找到 MRB缺料.xlsx")
