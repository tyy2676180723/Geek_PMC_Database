"""
共享工具模块：AgGrid 中文表格
新建看板时 import 本模块，调用 show_table / editable_table 即可。
"""
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, ColumnsAutoSizeMode
import pandas as pd

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
    "inRange": "范围",
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

_DEFAULT_H = 540

# FIT_CONTENTS 完成后（1000ms），把仍然过窄的列补到 80px
# 横向滚动条 position:fixed 固定在屏幕底部
_ON_READY_JS = JsCode("""
function(params) {
    // FIT_CONTENTS 自适应完成后补下限
    setTimeout(function() {
        var MIN_W = 80;
        params.columnApi.getAllColumns().forEach(function(col) {
            if (col.getActualWidth() < MIN_W)
                params.columnApi.setColumnWidth(col.getColId(), MIN_W);
        });
    }, 1000);

    // 横向滚动条固定到屏幕底部
    var hScroll  = document.querySelector('.ag-body-horizontal-scroll');
    var viewport = document.querySelector('.ag-body-viewport');
    if (!hScroll || !viewport) return;

    hScroll.style.position   = 'fixed';
    hScroll.style.bottom     = '0px';
    hScroll.style.zIndex     = '1000';
    hScroll.style.background = '#f0f2f6';
    hScroll.style.borderTop  = '1px solid #d0d0d0';

    function syncPos() {
        var r = viewport.getBoundingClientRect();
        hScroll.style.left  = r.left  + 'px';
        hScroll.style.width = r.width + 'px';
    }
    syncPos();
    window.addEventListener('resize', syncPos);
    window.addEventListener('scroll', syncPos);

    viewport.style.paddingBottom = (hScroll.offsetHeight || 20) + 'px';
}
""")

_GRID_BASE = dict(
    enableSorting=True,
    enableFilter=True,
    alwaysShowHorizontalScroll=True,
    suppressHorizontalScroll=False,
    domLayout="normal",
)


def _build_go(gb: GridOptionsBuilder) -> dict:
    gb.configure_grid_options(**_GRID_BASE)
    go = gb.build()
    go["localeText"] = LOCALE_ZH
    go["onFirstDataRendered"] = _ON_READY_JS
    return go


def show_table(df: pd.DataFrame, height: int = None, key: str = None) -> None:
    """只读表格：列菜单中文，FIT_CONTENTS 自适应，固定高度竖向滚动，横向滚动条固定在屏幕底部。"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True)
    go = _build_go(gb)
    AgGrid(df, gridOptions=go, height=height or _DEFAULT_H,
           use_container_width=True,
           columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
           allow_unsafe_jscode=True, key=key)


def editable_table(df: pd.DataFrame, editable_cols: list[str],
                   height: int = None, key: str = None) -> pd.DataFrame:
    """
    可编辑表格：列菜单中文，FIT_CONTENTS 自适应，固定高度竖向滚动，横向滚动条固定在屏幕底部。
    editable_cols：允许编辑的列名列表，其余列只读（黄色背景区分）。
    返回编辑后的 DataFrame。
    """
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, resizable=True,
                                sortable=True, filter=True)
    for col in editable_cols:
        if col in df.columns:
            gb.configure_column(col, editable=True,
                                cellStyle={"backgroundColor": "#fffde7"})
    go = _build_go(gb)
    result = AgGrid(df, gridOptions=go,
                    update_mode=GridUpdateMode.VALUE_CHANGED,
                    height=height or _DEFAULT_H,
                    use_container_width=True,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                    allow_unsafe_jscode=True, key=key)
    return pd.DataFrame(result["data"])
