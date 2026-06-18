# 导出策略

按使用场景分两档，避免「日常沟通也强制三格式 + 600 DPI」与「投稿缺格式」的冲突。

## 优先级

1. **用户 memory / 当前请求**中指定的格式 → 优先遵循。
2. 用户明确说「投稿 / 出版 / Nature / 600 DPI」→ **publication** 档。
3. 用户明确说「预览 / 沟通 / 组会 / 快速看一下」→ **communication** 档。
4. 均未说明 → 默认 **communication** 档（SVG + PNG）。

## Publication 档（投稿/出版）

适用：manuscript figure、supplementary figure、期刊投稿、用户要求出版级输出。

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
ggsave("figure.png", p, width = 3, height = 4, dpi = 600, units = "in")
ggsave("figure.pdf", p, width = 3, height = 4, units = "in")
ggsave("figure.svg", p, width = 3, height = 4, units = "in")
```

保存后运行 QC（publication 模式）：

```bash
python scripts/qc.py figure_name.png --mode publication
```

## Communication 档（日常沟通）

适用：快速预览、组会截图、聊天附件、迭代调试。

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

### R

```r
ggsave("figure.svg", p, width = 3, height = 4, units = "in")
ggsave("figure.png", p, width = 3, height = 4, dpi = 300, units = "in")
```

保存后运行 QC（communication 模式）：

```bash
python scripts/qc.py figure_name.png --mode communication
```

## 与 qc.py 的对应关系

| 检查项 | publication | communication |
|---|---|---|
| 最低 DPI | 600 | 300 |
| 要求 PDF | 是 | 否 |
| 要求 SVG | 是 | 是 |
| 空白率 / 尺寸 | 是 | 是 |

## 字体嵌入（两档共用）

无论哪一档，SVG/PDF 均须保证文字可编辑：

```python
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Arial'
```
