---
name: bioinformatics-plotting-standards
description: "生物信息学出版级数据可视化：火山图、热图、UMAP/t-SNE、violin、dotplot、Manhattan/GWAS、spatial、barplot 等；含简单 2–4 panel patchwork。务必在用户要画生信 plot/figure、DESeq2/scanpy/RNA-seq/scRNA-seq/spatial 结果出图、ComplexHeatmap/ggplot2/matplotlib 投稿导出（svg/png/pdf/600dpi）时使用。含 NMI pastel、色盲友好、adjustText/ggrepel、communication/publication 分层导出；默认 Python，提及投稿/出版/R/ComplexHeatmap 且未指定后端时先问 Python 还是 R。勿用于：非生信图表、只要表格不要图、plotly 交互 dashboard、hero panel 复杂投稿 figure（→ nature-figure）、pipeline/流程/示意图（→ GenerateImage）、英文润色/DA statement/PPT。"
---

# Bioinformatics Plotting Standards

创建符合 Nature/Cell/Science 要求的**生信数据图**标准：单张图 + **简单 2–4 panel 组合**（patchwork/subplot）。含 hero panel 的完整投稿 figure → `nature-figure` skill。

## 范围与路由

| 场景 | 处理 |
|---|---|
| 单张生信数据图 | 本 skill |
| 简单 2–4 panel 数据图组合 | 本 skill（patchwork / GridSpec） |
| 复杂投稿 figure、hero panel、figure contract | `nature-figure` |
| 流程图、示意图、大段文字信息图 | **GenerateImage** |
| 纯分析、表格即可 | 不出图；可**建议**出图，等用户确认 |

详见 [references/when-to-plot.md](references/when-to-plot.md)。

**默认原则**：不主动生成图；若图能显著帮助理解，可建议，用户确认后再画。

---

## 后端选择

**默认 Python**。用户提到投稿/出版/R/ComplexHeatmap 且未指定后端时，问 **「Python 还是 R？」** 后停止。选定后全程互斥。

详见 [references/backend-selection.md](references/backend-selection.md)。

---

## 绘图技术栈

### Python

| 库 | 角色 | 说明 |
|---|---|---|
| seaborn + matplotlib | 主要绘图库 | 默认 `ticks` 主题 |
| adjustText | 标签防重叠 | 火山图基因标注 |
| plotnine | 可选 | ggplot2 风格语法 |

### R

| 库 | 角色 | 说明 |
|---|---|---|
| ggplot2 + ggprism | 主绘图与学术主题 | |
| ComplexHeatmap | 热图 | 复杂注释 |
| ggrepel | 标签防重叠 | 等同 adjustText |
| patchwork | 子图拼接 | 简单 2–4 panel 数据图组合 |

---

## 核心工作流程

### 0. 确认是否出图 + 选择后端

1. 按 [when-to-plot.md](references/when-to-plot.md) 判断是否应创建图。
2. 按 [backend-selection.md](references/backend-selection.md) 确定 Python 或 R。

### 1. 环境初始化（必需，首先执行）

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Arial'
sns.set_theme(style="ticks")
```

> **`ticks` vs `white`**：`ticks` 保留刻度线、简洁学术；`white` 过空，`darkgrid` 不适合出版。

### 2. 创建图表

```python
fig, ax = plt.subplots(figsize=(3, 4), constrained_layout=True)
fig.set_constrained_layout_pads(w_pad=0.01, h_pad=0.01, wspace=0.02, hspace=0.01)
```

### 3. 设置文本样式

```python
ax.set_title("Title", fontsize=9, fontweight="bold")
ax.set_xlabel("X axis (units)", fontsize=8, fontweight="bold")
ax.set_ylabel("Y axis (units)", fontsize=8, fontweight="bold")
ax.tick_params(axis="both", labelsize=7)
plt.setp(ax.get_xticklabels(), rotation=45, ha="center", va="top")
ax.tick_params(axis="x", which="major", pad=3)
```

### 4. 选择配色方案

- **序列数据**：`plasma` / `plasma_r`（仅正值强度）
- **发散数据**：**Nature AD2024 紫–绿**（默认）；`RdBu_r` 仅当红蓝语义必要
- **UMAP / 多 cluster**：Nature AD2024 定性色（含棕 `#8C564B`）
- **分类对比（4–8 组）**：NMI Pastel
- **小提琴+箱线叠画**：Li Lab `pair` / `triple`
- **避免**：jet、rainbow、红绿组合

### 5. 移除不必要的边框

```python
sns.despine(ax=ax)
```

### 6. 添加文字标签（需要时）

详见 [文字标签系统](#文字标签系统)。

### 7. 导出并质量检查

按场景选择导出档，详见 [references/export-policy.md](references/export-policy.md)：

| 档位 | 触发 | 格式 |
|---|---|---|
| **publication** | 投稿/出版/用户要求 600 DPI | PNG 600 + PDF + SVG |
| **communication** | 默认；预览/沟通 | SVG + PNG 300（PDF 可选） |

```python
from pathlib import Path

out = Path("figure_name")
# publication 档示例：
fig.savefig(out.with_suffix(".png"), dpi=600, bbox_inches="tight")
fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
plt.close(fig)
```

QC：

```bash
python scripts/qc.py figure_name.png --mode publication
python scripts/qc.py figure_name.png --mode communication
```

---

## 文字标签系统

标签重叠是科学图表最常见问题之一。Python 用 **adjustText**，R 用 **ggrepel**。

### Python：adjustText

```python
from adjustText import adjust_text

texts = []
for _, row in top_genes.iterrows():
    texts.append(ax.text(
        row['log2FC'], -np.log10(row['pvalue']),
        row['gene_name'],
        fontsize=6, fontstyle='italic',
        ha='center', va='center'
    ))

adjust_text(texts, ax=ax,
            arrowprops=dict(arrowstyle='-', color='grey', lw=0.5),
            expand=(1.2, 1.4),
            force_text=(0.5, 0.8),
            force_points=(0.3, 0.5),
            only_move={'text': 'xy'})
```

### R：ggrepel

```r
library(ggplot2)
library(ggrepel)
library(ggprism)

ggplot(df, aes(x = log2FC, y = -log10(pvalue))) +
  geom_point(aes(color = significance), size = 0.8, alpha = 0.6) +
  geom_text_repel(
    data = top_genes, aes(label = gene_name),
    size = 2, fontface = "italic",
    max.overlaps = 20, segment.size = 0.3, segment.color = "grey50"
  ) +
  theme_prism(base_size = 8)
```

### 标签最佳实践

1. 一张图 **10–20** 个标签为上限
2. 基因名用**斜体**
3. 连接线 **0.3–0.5 pt** 灰色
4. 按显著性/效应量筛选，只标最重要的点
5. 标签字号 **5–6 pt**

---

## 质量检查流程

保存后运行 [scripts/qc.py](scripts/qc.py)。对标签重叠、配色等脚本无法检测项，Read 保存的 PNG 目视确认。

| 模式 | DPI | 要求 PDF |
|---|---|---|
| `--mode publication` | ≥ 600 | 是 |
| `--mode communication` | ≥ 300 | 否 |

---

## 快速参考模板

### Python（publication 档）

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Arial'
sns.set_theme(style="ticks")

fig, ax = plt.subplots(figsize=(3, 4), constrained_layout=True)
# ... 绘图 ...
ax.set_xlabel("X axis (units)", fontsize=8, fontweight="bold")
ax.set_ylabel("Y axis (units)", fontsize=8, fontweight="bold")
sns.despine(ax=ax)

out = Path("figure")
fig.savefig(out.with_suffix(".png"), dpi=600, bbox_inches="tight")
fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
plt.close(fig)
```

### R（ggplot2 + ggprism + ggrepel + patchwork）

```r
library(ggplot2)
library(ggprism)
library(ggrepel)
library(patchwork)

p <- ggplot(df, aes(x = x_var, y = y_var)) +
  geom_point(aes(color = group), size = 1.5, alpha = 0.7) +
  theme_prism(base_size = 8) +
  labs(x = "X axis (units)", y = "Y axis (units)", title = "Title")

ggsave("figure.png", p, width = 3, height = 4, dpi = 600, units = "in")
ggsave("figure.pdf", p, width = 3, height = 4, units = "in")
ggsave("figure.svg", p, width = 3, height = 4, units = "in")
```

---

## 关键参数速查

| 元素 | 推荐值 | 说明 |
|------|--------|------|
| 图表尺寸 | (3, 4) | 紧凑单图 |
| 标题字号 | 8-9 pt | 粗体 |
| 轴标签字号 | 7-8 pt | 粗体，含单位 |
| 刻度标签 | 6-7 pt | |
| 注释标签 | 5-6 pt | adjustText/ggrepel |
| PNG（投稿） | 600 DPI | publication 档 |
| PNG（沟通） | 300 DPI | communication 档 |
| 序列配色 | plasma | 仅正值强度 |
| 发散配色 | Nature 紫–绿 | 默认；`RdBu_r` 备选 |
| UMAP / 多 cluster | Nature AD2024 定性 | 含棕 `#8C564B` |
| 分类（多组 bar） | NMI Pastel | 见 color_schemes.md |
| 小提琴+箱线 | Li Lab pair/triple | 见 violin-boxplot.md |
| seaborn 主题 | ticks | |

---

## 详细参考文档

| 文件 | 用途 |
|---|---|
| [references/when-to-plot.md](references/when-to-plot.md) | 何时出图、GenerateImage 路由、与 nature-figure 边界 |
| [references/backend-selection.md](references/backend-selection.md) | Python/R 门禁与互斥规则 |
| [references/export-policy.md](references/export-policy.md) | publication / communication 分层导出 |
| [references/color_schemes.md](references/color_schemes.md) | 序列/发散/Nature AD2024/Li Lab/NMI Pastel |
| [references/violin-boxplot.md](references/violin-boxplot.md) | 小提琴+箱线叠画（matplotlib 推荐、配色、参数） |
| [references/journal_requirements.md](references/journal_requirements.md) | Nature/Cell/Science 尺寸与字体 |
| [references/troubleshooting.md](references/troubleshooting.md) | 标签重叠、截断、colorbar 等 |

---

## 最终检查清单

- [ ] 确认任务属于单图或简单 2–4 panel（非 hero/contract 投稿页 → nature-figure）
- [ ] 未主动出图；若建议了出图则已获用户确认
- [ ] 后端已选定（默认 Python；投稿/R 场景已确认）
- [ ] 字体与 `ticks` 主题已在绘图前设置
- [ ] 配色色盲友好；发散热图默认 Nature 紫–绿；UMAP 用定性色（含棕）；violin+box 用 Li Lab
- [ ] 导出档正确（publication 或 communication）
- [ ] 标签无重叠；基因名斜体
- [ ] `sns.despine()`；轴标签含单位
- [ ] QC 已通过（`scripts/qc.py --mode ...`）
