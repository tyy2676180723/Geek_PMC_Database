"""
共享工具模块：AgGrid 中文表格
新建看板时 import 本模块，调用 show_table / editable_table 即可。
"""
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
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

# 首次渲染：先自适应列宽，再把超 100px 的列压回 100px；不设 maxWidth，手动拖拽不受限
# minWidth=80 保证内容极短的列也不会被压到难以辨认
_CAP_COLUMNS_JS = JsCode("""
function(params) {
    var MIN_W = 80, MAX_W = 100;
    params.columnApi.autoSizeAllColumns();
    params.columnApi.getAllColumns().forEach(function(col) {
        var w = col.getActualWidth();
        if (w < MIN_W) {
            params.columnApi.setColumnWidth(col.getColId(), MIN_W);
        } else if (w > MAX_W) {
            params.columnApi.setColumnWidth(col.getColId(), MAX_W);
        }
    });
}
""")

_ROW_H       = 40   # gridOptions 里显式设定的行高，计算和渲染保持一致
_HEADER_H    = 48   # 同上，显式设定的列头高度
_H_SCROLL    = 20   # 水平滚动条高度
_FRAME_PAD   = 10   # iframe 自身的边距 buffer
_MAX_H       = 520  # 最大 iframe 高度（超出后竖向滚动）


def _calc_height(df: pd.DataFrame) -> int:
    return min(_HEADER_H + len(df) * _ROW_H + _H_SCROLL + _FRAME_PAD, _MAX_H)


_GRID_BASE = dict(
    enableSorting=True,
    enableFilter=True,
    alwaysShowHorizontalScroll=True,
    suppressHorizontalScroll=False,
    rowHeight=_ROW_H,       # 显式行高，与计算公式匹配
    headerHeight=_HEADER_H, # 显式列头高度，与计算公式匹配
)


def _build_go(gb: GridOptionsBuilder) -> dict:
    gb.configure_grid_options(**_GRID_BASE)
    go = gb.build()
    go["localeText"] = LOCALE_ZH
    go["onFirstDataRendered"] = _CAP_COLUMNS_JS
    return go


def show_table(df: pd.DataFrame, height: int = None, key: str = None) -> None:
    """只读表格：列菜单中文，竖向滚动，横向滚动条始终可见，列宽 80~100px。"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True)
    go = _build_go(gb)
    AgGrid(df, gridOptions=go, height=height or _calc_height(df),
           use_container_width=True, fit_columns_on_grid_load=False,
           allow_unsafe_jscode=True, key=key)


def editable_table(df: pd.DataFrame, editable_cols: list[str],
                   height: int = None, key: str = None) -> pd.DataFrame:
    """
    可编辑表格：列菜单中文，竖向滚动，横向滚动条始终可见，列宽 80~100px。
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
                    height=height or _calc_height(df),
                    use_container_width=True, fit_columns_on_grid_load=False,
                    allow_unsafe_jscode=True, key=key)
    return pd.DataFrame(result["data"])
