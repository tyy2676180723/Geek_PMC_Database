import json
import subprocess
from datetime import date

import streamlit as st
import pandas as pd
from pathlib import Path

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


def merge_progress(df: pd.DataFrame, sheet_name: str, prog: dict) -> pd.DataFrame:
    """将已保存的处理进度合并到 df，若无「处理进度」列则新增。"""
    key_col = "物料编码" if "物料编码" in df.columns else df.columns[0]
    mapping = prog.get(sheet_name, {})
    df = df.copy()
    df["处理进度"] = df[key_col].astype(str).map(mapping).fillna("")
    return df, key_col


def shortage_editor(df_raw: pd.DataFrame, sheet_name: str, prog: dict, editor_key: str):
    """渲染可编辑的缺料表，返回 (edited_df, key_col)。"""
    df, key_col = merge_progress(df_raw, sheet_name, prog)

    # 所有列禁用，仅「处理进度」可编辑
    col_cfg = {c: st.column_config.Column(disabled=True) for c in df.columns if c != "处理进度"}
    col_cfg["处理进度"] = st.column_config.TextColumn("处理进度", help="可直接编辑，点击保存后生效")

    edited = st.data_editor(df, column_config=col_cfg, use_container_width=True, height=400, key=editor_key)
    return edited, key_col


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
        prog = load_progress()
        xls2 = pd.ExcelFile(xls_path2)
        sheets2 = {name: pd.read_excel(xls2, sheet_name=name) for name in xls2.sheet_names}
        sub_a, sub_b = st.tabs(xls2.sheet_names)

        with sub_a:
            sname = xls2.sheet_names[0]
            df_a = sheets2[sname]
            st.metric("缺料物料数", len(df_a))
            edited_a, key_a = shortage_editor(df_a, sname, prog, "editor_shortage_a")
            if st.button("💾 保存处理进度", key="save_a", type="primary"):
                prog[sname] = dict(zip(edited_a[key_a].astype(str), edited_a["处理进度"]))
                save_progress(prog)
                st.success("已保存并推送")

        with sub_b:
            sname2 = xls2.sheet_names[1]
            df_b = sheets2[sname2]
            st.metric("待开工缺料数", len(df_b))
            edited_b, key_b = shortage_editor(df_b, sname2, prog, "editor_shortage_b")
            if st.button("💾 保存处理进度", key="save_b", type="primary"):
                prog[sname2] = dict(zip(edited_b[key_b].astype(str), edited_b["处理进度"]))
                save_progress(prog)
                st.success("已保存并推送")
    else:
        st.warning("未找到 MRB缺料.xlsx")
