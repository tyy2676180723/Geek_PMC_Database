# AgGrid 最后一行被遮挡问题 — 解决方案

## 问题现象

Streamlit + streamlit-aggrid 表格，滚动到最底部时，**最后一行数据只显示一半**，无法通过鼠标滚轮完整显示（但用键盘方向键可以定位到）。

## 根本原因

`position: fixed; bottom: 0` 的横向滚动条脱离了 AG Grid 的 flex 布局，叠在 iframe 底部，
遮住了最后一行数据的下半部分。AG Grid 内部计算的 `maxScrollTop` 不能滚到足够低的位置，
导致最后一行永远无法完整呈现。

## 解决方案：幽灵钉住行（Pinned Bottom Spacer Row）

在 AG Grid 底部加一个**不可见的 Pinned Bottom Row**，高度 **28px**，作为缓冲垫，
把最后一行真实数据顶到横向滚动条上方。

Pinned Row 的特性：
- 不参与排序、筛选
- 不影响 `result["data"]` 返回的数据
- 通过 CSS 隐藏 `.ag-floating-bottom`，用户完全看不到它

---

## 具体实现

### 1. 在 `utils.py` 中添加以下代码

#### 1-A：幽灵行高度回调（JS）

```python
from st_aggrid import JsCode

_PINNED_ROW_HEIGHT_JS = JsCode("""
function(params) {
    if (params.node.rowPinned === 'bottom') return 28;
    return null;
}
""")
```

#### 1-B：在 `_build_go` 函数中注册幽灵行

```python
def _build_go(gb):
    # ... 原有配置 ...
    go = gb.build()
    go["localeText"] = LOCALE_ZH
    go["onFirstDataRendered"] = _ON_READY_JS
    go["pinnedBottomRowData"] = [{}]          # 空数据行
    go["getRowHeight"]        = _PINNED_ROW_HEIGHT_JS
    return go
```

#### 1-C：在 `_ON_READY_JS` 中注入 CSS 隐藏幽灵行

在 `onFirstDataRendered` 的 JS 函数体内加入：

```javascript
// 用 CSS 隐藏幽灵钉住行（getRowStyle 对 pinned 行不生效）
var st = document.getElementById('__ag_ghost__');
if (!st) {
    st = document.createElement('style');
    st.id = '__ag_ghost__';
    document.head.appendChild(st);
}
st.textContent = '.ag-floating-bottom { opacity: 0 !important; pointer-events: none !important; }';
```

---

## 高度校准方法

28px 是在以下环境测试得出的最佳值：

| 环境 | 值 |
|---|---|
| 浏览器 | Chrome（Windows 11） |
| 横向滚动条高度 | ~20px（position:fixed） |
| 表格默认高度 | 540px（部分看板 500px） |
| 幽灵行高度 | **28px** |

**如果新看板最后一行仍显示不全，逐步调整 `return 28` 的数值：**
- 差一点点（2-3px）→ 改为 30
- 差半行（10-14px）→ 改为 38-40
- 完全显示但底部有明显空白 → 减小数值

**调整依据**：幽灵行高度 ≈ `position:fixed` 横向滚动条高度 + 几像素安全余量。

---

## 注意事项

1. `getRowStyle` 对 pinned 行在 streamlit-aggrid 0.3.4.post3 中**不生效**，
   必须用 CSS 注入 `.ag-floating-bottom { opacity: 0 }` 来隐藏。

2. `editable_table` 返回 `pd.DataFrame(result["data"])`，
   `pinnedBottomRowData` 的数据在 `result["pinnedBottomRows"]` 中，
   不会混入返回值，**无需额外过滤**。

3. 如果看板使用了自定义 `height` 参数（如 `height=500`），
   幽灵行高度可能需要比默认值（28px）稍大一点。

---

## 参考文件

| 文件 | 说明 |
|---|---|
| `utils.py` | 当前生效版本（28px 幽灵行 + position:fixed 横向滚动条） |
| `utils_backup1_scrollbar.py` | 旧版：position:fixed 横向滚动条正常，最后一行有问题 |
| `utils_backup2_pinned.py` | 新版：13px 幽灵行最后一行正常，无横向滚动条（无 fixed） |
