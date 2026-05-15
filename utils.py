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

# 用 IntersectionObserver 监听 grid 真正可见后再自适应列宽
# 等价于手动点击列菜单的"所有列自适应"，但自动触发
_ON_READY_JS = JsCode("""
function(params) {
    var grid = document.querySelector('.ag-root-wrapper');

    // Force horizontal scrollbar to always occupy layout space so the flex row
    // area is sized correctly and the last row is never hidden underneath it.
    var st = document.getElementById('__ag_hscroll__');
    if (!st) {
        st = document.createElement('style');
        st.id = '__ag_hscroll__';
        document.head.appendChild(st);
    }
    st.textContent =
        '.ag-body-horizontal-scroll { display: block !important; min-height: 17px !important; }' +
        '.ag-body-horizontal-scroll-viewport { min-height: 17px !important; overflow-x: scroll !important; }';

    function autoSize() {
        params.columnApi.autoSizeAllColumns();
    }

    if (grid && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    setTimeout(autoSize, 100);
                    observer.disconnect();
                }
            });
        }, { threshold: 0.1 });
        observer.observe(grid);
    } else {
        setTimeout(autoSize, 600);
    }
}
""")

_GRID_BASE = dict(
    enableSorting=True,
    enableFilter=True,
    alwaysShowHorizontalScroll=True,
    suppressHorizontalScroll=False,
    domLayout="normal",
    stopEditingWhenCellsLoseFocus=True,
    suppressColumnVirtualisation=True,
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
