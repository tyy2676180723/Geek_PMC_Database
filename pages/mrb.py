import json
import subprocess
from datetime import date

import streamlit as st
import pandas as pd
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("MRB 看板")

BASE = Path(__file__).parent.parent
PROGRESS_FILE = BASE / "mrb_progress.json"

LOCALE_ZH = {
    "sortAscending": "升序",
    "sortDescending": "降序",
    "noSort": "不排序",
    "autosizeThisColumn": "自适应列宽",
    "autosizeAllColumns": "所有列自适应",
    "pinColumn": "固定列",
    "pinLeft": "固定到左侧",
    "pinRight": "固定到右侧",
    "noPin": "取消固定",
    "hideColumn": "隐藏列",
    "chooseColumns": "选择列",
    "resetColumns": "重置列",
    "export": "导出",
    "csvExport": "导出 CSV",
    "excelExport": "导出 Excel",
    "filterOoo": "筛选...",
    "equals": "等于",
    "notEqual": "不等于",
    "lessThan": "小于",
    "greaterThan": "大于",
    "lessThanOrEqual": "小于等于",
    "greaterThanOrEqual": "大于等于",
    "contains": "包含",
    "notContains": "不包含",
    "startsWith": "开头为",
    "endsWith": "结尾为",
    "blank": "空",
    "notBlank": "非空",
    "andCondition": "且",
    "orCondition": "或",
    "clearFilter": "清除",
    "applyFilter": "应用",
    "noRowsToShow": "暂无数据",
    "loadingOoo": "加载中...",
    "columns": "列",
    "filters": "筛选",
    "page": "页",
    "of": "/",
    "to": "-",
    "more": "更多",
    "next": "下一页",
    "last": "末页",
    "first": "首页",
    "previous": "上一页",
}


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


def shortage_editor(df_raw: pd.DataFrame, sheet_name: str, prog: dict, editor_key: str):
    df, key_col = merge_progress(df_raw, sheet_name, prog)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, resizable=True, sortable=True, filter=True)
    gb.configure_column("处理进度", editable=True,
                        cellStyle={"backgroundColor": "#fffde7"})
    gb.configure_grid_options(enableSorting=True, enableFilter=True)
    go = gb.build()
    go["localeText"] = LOCALE_ZH

    result = AgGrid(
        df,
        gridOptions=go,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        height=400,
        use_container_width=True,
        key=editor_key,
    )
    edited_df = pd.DataFrame(result["data"])
    return edited_df, key_col


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
