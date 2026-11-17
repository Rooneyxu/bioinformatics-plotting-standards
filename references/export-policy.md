# 导出策略与排版档位（Thesis / Publication / Communication）

按目标载体分三档，既保证**近期默认符合北大毕业论文统一字号与 1:1 版心规范**，又完整保留**英文 SCI 期刊投稿**与**日常组会沟通**两套原有工作流。

## 档位路由优先级

1. **用户请求中明确指定的格式或参数** → 最高优先级遵循。
2. 用户明确提及具体**英文期刊 / SCI 投稿**（如 `Nature`、`NMI`、`Cell`、`Science`、`manuscript submission`）→ **`publication` 档**（期刊尺寸 + 期刊面板标签规范）。
3. 用户明确提及**组会 / 预览 / 沟通 / 快速看一下** → **`communication` 档**（SVG + 300 DPI PNG，轻量快速）。
4. **近期默认（未提英文期刊且未提组会预览，或明确提及毕业论文 / 学位论文 / thesis）** → **`thesis` 档**（1:1 适配北大 `15.80 cm` 版心 + 扁平 `7.5 pt` 统一字号 + `10 pt` 大写 `A, B, C, D`）。

---

## 1. Thesis 档（近期默认 · 学位论文规范）

详见 [thesis-format.md](thesis-format.md)。核心目标是**原大插入 Word 不缩放，跨图字号高度一致，全员严格 $\le$ 五号字（`10.5 pt`）**。

| 项目 | 规范要求 |
|---|---|
| **画布物理宽度** | 按内容自由设定，**最大宽度 $\le 6.20\text{ in}$ (`15.75 cm`)** 以避免被 Word 自动缩小（常用参考预设：`6.20 / 4.20 / 3.00 in`）；100% 原大插入 Word |
| **字号体系（扁平 7.5pt）** | 大写面板字母 **`A, B, C, D` = `10.0 pt` Arial Bold**；子图标题 **`8.5 pt` Bold**；坐标轴/刻度/图例/常规注释 **统一 `7.5 pt`（六号字）**（密集标注特例 `6.5 pt`） |
| **导出格式** | **600 DPI PNG + 可编辑 PDF + 可编辑 SVG** |

### Python（推荐直接用 `scripts/thesis_style.py`）

```python
from scripts.thesis_style import create_thesis_figure, add_panel_labels, save_thesis_figure

fig, axes = create_thesis_figure(width_tier="full", height_in=3.0, nrows=1, ncols=2)
# ... 绘图 ...
add_panel_labels(fig, axes)          # 统一 10.0 pt Arial Bold 大写 A, B
save_thesis_figure(fig, "figure_name")
```

保存后运行毕业论文专项质检（含 PDF 真实字号 `<= 10.5 pt` 与大写面板字母一致性扫描）：

```bash
python scripts/qc.py figure_name.png --mode thesis
```

---

## 2. Publication 档（英文 SCI 期刊投稿）

适用：明确面向英文期刊投稿（*Nature*, *Cell*, *Science*, *NMI* 等）的 manuscript figure / supplementary figure。

| 格式 | 要求 |
|---|---|
| PNG | **600 DPI**，`bbox_inches='tight'` |
| PDF | 必须，字体可编辑（`pdf.fonttype=42`） |
| SVG | 必须，字体可编辑（`svg.fonttype='none'`） |

### Python

```python
from pathlib import Path

out = Path("figure_name")
fig.savefig(out.with_suffix(".png"), dpi=600, bbox_inches="tight")
fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
plt.close(fig)
```

### R

```r
ggsave("figure.png", p, width = 3.5, height = 3.5, dpi = 600, units = "in")
ggsave("figure.pdf", p, width = 3.5, height = 3.5, units = "in", device = cairo_pdf)
ggsave("figure.svg", p, width = 3.5, height = 3.5, units = "in")
```

保存后运行 QC（publication 模式）：

```bash
python scripts/qc.py figure_name.png --mode publication
```

---

## 3. Communication 档（日常沟通 / 组会预览）

适用：快速预览、组会截图、聊天附件、探索性迭代调试。

| 格式 | 要求 |
|---|---|
| SVG | 必须 |
| PNG | 必须，**300 DPI** 即可（非 600） |
| PDF | 可选，用户未要求则不强制 |

### Python

```python
from pathlib import Path

out = Path("figure_name")
fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
fig.savefig(out.with_suffix(".png"), dpi=300, bbox_inches="tight")
plt.close(fig)
```

保存后运行 QC（communication 模式）：

```bash
python scripts/qc.py figure_name.png --mode communication
```

---

## 与 `qc.py` 的对应关系

| 检查项 | `thesis`（近期默认） | `publication`（SCI 期刊） | `communication`（日常沟通） |
|---|---|---|---|
| 最低 DPI | 600 | 600 | 300 |
| 要求 PDF & SVG | 是 | 是 | 仅要求 SVG |
| 版心宽度 $> 6.22\text{ in}$ (`15.80 cm`) | **`[WARN]` 提醒**（防竖排页自动缩小） | 否（按期刊单/双栏） | 否 |
| PDF 字形 $\le 10.5\text{ pt}$（五号字） | **是（阻断式）** | 否 | 否 |
| 面板字母大写 `A/B/C/D` 及一致性 | **是（阻断式）** | 按目标期刊（如 Nature 小写） | 否 |

## 字体嵌入（三档共用）

无论哪一档，SVG/PDF 均须保证文字可编辑：

```python
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'SimHei', 'DejaVu Sans']
```
