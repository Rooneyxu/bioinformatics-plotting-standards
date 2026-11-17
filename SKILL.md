---
name: bioinformatics-plotting-standards
description: "生物信息学出版与学位论文级数据可视化：火山图、热图、UMAP/t-SNE、violin、dotplot、Manhattan/GWAS、spatial、barplot，以及云雨图、哑铃图、山脊图、棒棒糖图、异构相关矩阵、桑基冲积图、Funkyheatmap、UpSet、SHAP 蜂群图等进阶图型选型；含简单 2–4 panel patchwork。近期默认启用毕业论文 thesis 规范（15.8cm 1:1 版心、扁平 7.5pt 统一字号≤五号字、大写 10pt A/B/C/D），同时完整保留 SCI 期刊 publication 与组会 communication 分层导出；默认 Python，提及英文期刊投稿/R/ComplexHeatmap 且未指定后端时先问 Python 还是 R。勿用于：非生信图表、只要表格不要图、plotly 交互 dashboard、hero panel 复杂投稿 figure（→ nature-figure）、pipeline/流程/示意图（→ figgenie-paper-diagram 或 GenerateImage）、英文润色/DA statement/PPT。"
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

> **库选型原则**：优先复用标准栈（`matplotlib`/`seaborn` 或 `ggplot2`/`patchwork`）与已装成熟库；进阶图型若需本机未安装的第三方包（如 `upsetplot`、`shap`、`funkyheatmap`、`ggalluvial`、`ggdist`），先向用户说明包名与优势、确认后再安装，不手写脆弱拼接。

### Python

| 库 | 角色 | 说明 |
|---|---|---|
| seaborn + matplotlib | 主要绘图库 | 默认 `ticks` 主题；含 `PairGrid`/`JointGrid`/极坐标/GridSpec |
| adjustText | 标签防重叠 | 火山图、散点、帕累托图基因/方法标注 |
| upsetplot / shap / pycirclize | 进阶专项图（按需） | 多集合 UpSet、SHAP 蜂群图、弦图 |
| plotnine | 可选 | ggplot2 风格语法 |

### R

| 库 | 角色 | 说明 |
|---|---|---|
| ggplot2 + ggprism | 主绘图与学术主题 | |
| ComplexHeatmap / funkyheatmap | 热图与综合评测表 | 复杂注释热图 / 方法学多指标多几何编码总表 |
| ggdist / ggridges | 分布与梯度 | 云雨图（Raincloud）/ 山脊图（Ridgeline） |
| ggalluvial / ComplexUpset / circlize | 流向、集合与网络 | 桑基冲积图、≥4 组交集 UpSet、弦图 |
| GGally / corrplot | 多变量相关 | 异构混合相关矩阵（Correlogram） |
| ggrepel | 标签防重叠 | 等同 adjustText |
| patchwork | 子图拼接 | 简单 2–4 panel 数据图组合 |

---

## 核心工作流程

### 0. 确认是否出图 + 图型选型 + 选择后端

1. **是否出图**：按 [when-to-plot.md](references/when-to-plot.md) 判断是否应创建图。
2. **图型选型（Chart Selection）**：
   - 用户**已明确点名图型**（如「画火山图」「画 barplot」「画热图」）→ 按指定图型执行；仅在可读性硬伤（如 $\ge 4$ 集合画 Venn、上万散点严重过绘）时附一句升级建议。
   - 用户**仅描述数据或分析目标、未锁死基础图型**，或询问怎么画更丰富/出彩 → **必须先查下方选型表与 [references/chart-selection.md](references/chart-selection.md)**，按数据形态匹配高信息密度图型（建议出图时也直接推荐匹配后的进阶图型，避免默认退回纯箱线图、误差棒粗柱状图或单一色块热图）：

| 数据形态 / 论证目标 | 优先选用的高表现力图型 | 替代的平庸默认 |
|---|---|---|
| 多组连续分布（含双峰/偏态/样本量差异） | **云雨图（Raincloud）** 或 **Li Lab 小提琴+箱线叠画** | 纯箱线图 / 误差棒柱图 |
| 同一批数据集/样本在前后两状态的成对变化 | **配对哑铃图 / 斜率图（Dumbbell / Slopegraph）** | 并排分组柱状图 |
| 连续变量沿空间/伪时间/噪声梯度的多组推移 | **山脊图（Ridgeline / Joyplot，4–12 层）** | 多条缠绕折线 / 并排箱线 |
| 单维数值排名（消融增益、重要性、富集得分） | **排序棒棒糖图（Ordered Lollipop，按值排序）** | 粗重柱状图 |
| 3–8 个连续变量成对相关（跨平台/重复/特征正交） | **异构混合相关矩阵（Asymmetric Correlogram：下三角 2D KDE+拟合，对角线密度，上三角相关气泡）** | 纯色块热图 / 过绘散点矩阵 |
| 大样本双变量关系（$>1000$ 点）+ 单变量分布 | **2D KDE 等高线 / Hexbin + 边际密度图（Marginal Plot）** | 普通不透明散点图 |
| 多方法 × 多数据集/多维度指标综合 Benchmark | **Funkyheatmap（多几何编码表）** 或 **分轴归一化雷达图（$\le 4$ 方法）** | 单一色块指标热图 / 大表格 |
| 算法精度 vs 耗时/显存的可扩展性权衡 | **帕累托前沿气泡图（Pareto Frontier Bubble）** | 分开的精度柱图 + 时间柱图 |
| $\ge 4$ 个基因集/检出集的交集结构 | **UpSet Plot**（可叠定量属性子面板） | 四叶/五叶韦恩图 |
| 聚类簇对应、标签重分配、跨层生物学映射 | **冲积图 / 桑基图（Alluvial / Sankey）**；对称共定位用 **弦图（Chord）** | 混淆矩阵色块 |
| 机器学习/多模态特征重要性与正负作用方向 | **SHAP 蜂群图（Beeswarm Plot）** | 平均值特征重要性柱图 |

3. **确定目标档位（Format Tier）**：按 [export-policy.md](references/export-policy.md) 路由：
   - **`thesis`（近期默认 · 北大学位论文规范）**：未指明英文期刊且非组会快速预览时默认启用，详见 [references/thesis-format.md](references/thesis-format.md) 与 `scripts/thesis_style.py`。
   - **`publication`（英文 SCI 期刊档）**：明确提及 *Nature* / *NMI* / *Cell* / *Science* / 英文期刊投稿时启用。
   - **`communication`（日常沟通档）**：明确提及组会、快速预览、聊天看效果时启用。
4. **选择后端**：按 [backend-selection.md](references/backend-selection.md) 确定 Python 或 R。

### 1–3. 环境初始化、画布尺寸与统一字号（区分档位）

#### A. 近期默认：`thesis` 毕业论文档（最大宽度 $\le 6.20\text{ in}$ 免缩放 + 扁平 `7.5 pt` 统一字号）

- **画布宽度随内容自由设定，上限 $\le 6.20\text{ in}$ (`15.75 cm`)**：适配北大 A4 竖排净版心 `15.80 cm = 6.22 in`，避免被 Word 自动缩小，100% 原大插入即可保持跨图字号一致（可选用常用参考预设 `full=6.20 in` / `medium=4.20 in` / `half=3.00 in`，也可直接传任意 `width_in`）。
- **扁平 `7.5 pt` 统一字号阶梯**（全员严格 $\le$ 五号字 `10.5 pt`，图内文字英文为主 + `Arial`）：
  - **组图面板字母 `A, B, C, D`**：固定 **`10.0 pt` `Arial Bold`（大写）**，跨图字体字号 100% 一致；单图不加面板字母
  - **子图标题（Panel Title）**：**`8.5 pt` `Arial Bold`**（非必要可省略）
  - **其余图内文字全员统一**：坐标轴标题、刻度数字、图例、*p* 值与常规标注 **统一 `7.5 pt`（六号字，常规字重）**；仅超密基因/点标注特例可降至 `6.5 pt`（硬下限 `6.0 pt`）
- **细节格式规范（北大模板要求）**：
  - **统计符号斜体**：显著性与统计量（`*p*`、`*n*`、`*r*`、`*t*`）统一用斜体（如 `format_stat_p(p)` 或 `r"$\it{p}$ = ..."`）；
  - **单位与空格**：摩尔浓度统一用 **`mol/L`**（如 `mmol/L`、`μmol/L`，禁用 `M/mM/μM`）；数字与单位间留一个半角空格（如 `10 μm`、`5 mL`），**`%` 和 `℃` 除外**（如 `50%`、`37℃`）；
  - **多曲线点型区分**：同一图内多条折线除颜色外，须搭配不同形状的 marker（`THESIS_MARKERS = ["o", "s", "^", "D", "v", "P"]`）或线型；
  - **无物理意义坐标轴**：UMAP / t-SNE / 空间原位图直接移除无意义的刻度数字与刻度线（`strip_meaningless_ticks(ax)`）。

```python
# 推荐直接复用内置样式模块（也可将对应常量内联到独立脚本中）
from scripts.thesis_style import (
    THESIS_FONT_SIZES,
    create_thesis_figure,
    add_panel_labels,
    save_thesis_figure,
)

# 自动完成 Arial 字体、ticks 主题、layout="constrained" 与扁平 7.5pt 字号初始化
fig, axes = create_thesis_figure(width_tier="full", height_in=2.8, nrows=1, ncols=2)
```

#### B. 英文 SCI 期刊 `publication` 档 / 组会 `communication` 档（完整保留）

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Arial'
sns.set_theme(style="ticks")

fig, ax = plt.subplots(figsize=(3.5, 3.5), constrained_layout=True)
ax.set_title("Title", fontsize=8.5, fontweight="bold")
ax.set_xlabel("X axis (units)", fontsize=7.5)
ax.set_ylabel("Y axis (units)", fontsize=7.5)
ax.tick_params(axis="both", labelsize=7)
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

按场景选择导出档，详见 [references/export-policy.md](references/export-policy.md) 与 [references/thesis-format.md](references/thesis-format.md)：

| 档位 | 触发条件 | 画布与格式要求 |
|---|---|---|
| **`thesis`（近期默认）** | 未提具体英文期刊且非组会预览；或提毕业论文/学位论文 | 宽度自由设定且 $\le 6.20\text{ in}$ (`15.75 cm`)；PNG 600 + PDF + SVG |
| **`publication`** | 明确提 *Nature* / *Cell* / *NMI* / 英文期刊投稿 | 期刊单/双栏尺寸；PNG 600 + PDF + SVG |
| **`communication`** | 明确提组会 / 快速预览 / 沟通 | SVG + PNG 300（PDF 可选） |

```python
# thesis 默认档导出示例（锁定物理宽度，原大插入 Word 不变形）：
add_panel_labels(fig, axes)        # 多面板组图统一打 10.0 pt Arial Bold 大写 A, B...
save_thesis_figure(fig, "figure_name")
```

QC（必跑）：

```bash
python scripts/qc.py figure_name.png --mode thesis         # 近期默认：含 PDF 字号<=10.5pt 与大写 A/B/C/D 校验
python scripts/qc.py figure_name.png --mode publication    # 英文期刊投稿
python scripts/qc.py figure_name.png --mode communication  # 组会快速预览
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
5. 标签字号：`thesis` 默认档常规标注统一 **`7.5 pt`**（超密基因标签特例 `6.5 pt`）；英文期刊紧凑单图 `5.5–6.5 pt`
6. **Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.** 少加副标题、口号式文案、说明框或重复图例的注释；分组、对比和重点用布局、视觉层级、配色表达

---

## 质量检查流程

保存后运行 [scripts/qc.py](scripts/qc.py)。对标签重叠、配色等脚本无法检测项，Read 保存的 PNG 目视确认。

| 模式 | DPI | 要求 PDF | 额外硬核校验 |
|---|---|---|---|
| `--mode thesis`（近期默认） | ≥ 600 | 是 | PDF 全字形 $\le 10.5\text{ pt}$（五号字）、大写 `A/B/C/D` 字体字号一致、超 `6.22 in` 宽度 `[WARN]` 提醒 |
| `--mode publication` | ≥ 600 | 是 | 矢量导出完整性与留白检查 |
| `--mode communication` | ≥ 300 | 否 | 基础分辨率与留白检查 |

---

## 快速参考模板

### Python（`thesis` 近期默认档）

```python
from scripts.thesis_style import (
    THESIS_FONT_SIZES,
    create_thesis_figure,
    add_panel_labels,
    save_thesis_figure,
)
import seaborn as sns

# 单图用 width_tier="medium" (4.20 in)；通栏组图用 width_tier="full" (6.20 in)
fig, ax = create_thesis_figure(width_tier="medium", height_in=2.8)
# ... 绘图（坐标轴/刻度/图例自动统一 7.5 pt）...
ax.set_xlabel("X axis (units)")
ax.set_ylabel("Y axis (units)")
sns.despine(ax=ax)

save_thesis_figure(fig, "figure")
```

### R（`thesis` 近期默认档：ggplot2 + patchwork）

```r
library(ggplot2)
library(ggrepel)
library(patchwork)

theme_thesis <- theme_classic(base_size = 7.5, base_family = "Arial") +
  theme(
    plot.title = element_text(size = 8.5, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 7.5, colour = "black"),
    axis.text = element_text(size = 7.5, colour = "black"),
    legend.title = element_text(size = 7.5),
    legend.text = element_text(size = 7.5),
    legend.background = element_blank()
  )

p <- ggplot(df, aes(x = x_var, y = y_var)) +
  geom_point(aes(color = group), size = 1.5, alpha = 0.7) +
  theme_thesis +
  labs(x = "X axis (units)", y = "Y axis (units)")

# 居中单图 4.20 in；若为 patchwork 组图则加 plot_annotation(tag_levels = 'A') & theme(plot.tag = element_text(size = 10, face = 'bold', family = 'Arial')) 并用 width = 6.20
ggsave("figure.png", p, width = 4.20, height = 2.80, dpi = 600, units = "in")
ggsave("figure.pdf", p, width = 4.20, height = 2.80, units = "in", device = cairo_pdf)
ggsave("figure.svg", p, width = 4.20, height = 2.80, units = "in")
```

---

## 关键参数速查

| 元素 | `thesis` 近期默认（学位论文） | `publication`（英文期刊） | 说明 |
|------|--------|--------|------|
| 画布物理宽度 | **自由设定且 $\le 6.20\text{ in}$**（参考预设 `6.2/4.2/3.0`） | 单栏 `3.5 in` / 双栏 `7.0 in` | `≤ 15.8cm` 原大插入 Word 不被自动缩小 |
| 组图面板字母 | **大写 `A, B, C, D` (`10.0 pt` Bold)** | 按期刊（Nature 小写 `8 pt`） | 全文必须一致，Arial Bold |
| 子图标题 | **`8.5 pt` Bold** | `8–9 pt` Bold | 非必要可省略 |
| 轴标题 / 刻度 / 图例 | **统一 `7.5 pt`（六号字）** | 轴 `7–8 pt` / 刻度 `6–7 pt` | 扁平化消除跨图字号参差 |
| 图内常规注释 | **`7.5 pt`**（超密特例 `6.5 pt`） | `5.5–6.5 pt` | 绝不超过五号 `10.5 pt` |
| PNG 分辨率 | **600 DPI** | 600 DPI（沟通档 300） | |
| 序列配色 | plasma | plasma | 仅正值强度 |
| 发散配色 | Nature 紫–绿 | Nature 紫–绿 | 默认；`RdBu_r` 备选 |
| UMAP / 多 cluster | Nature AD2024 定性 | Nature AD2024 定性 | 含棕 `#8C564B` |
| 分类（多组 bar） | NMI Pastel | NMI Pastel | 见 color_schemes.md |
| 小提琴+箱线 | Li Lab pair/triple | Li Lab pair/triple | 见 violin-boxplot.md |
| seaborn 主题 | ticks | ticks | |

---

## 详细参考文档

| 文件 | 用途 |
|---|---|
| [references/thesis-format.md](references/thesis-format.md) | **北大学位论文 1:1 版心宽度、扁平 7.5pt 统一字号与大写 A/B/C/D 规范（近期默认）** |
| [references/when-to-plot.md](references/when-to-plot.md) | 何时出图、GenerateImage 路由、与 nature-figure 边界 |
| [references/chart-selection.md](references/chart-selection.md) | **进阶图型选型与避坑指南**（云雨图、哑铃图、山脊图、异构相关矩阵、Funkyheatmap、UpSet、冲积桑基图、SHAP 等） |
| [references/backend-selection.md](references/backend-selection.md) | Python/R 门禁与互斥规则 |
| [references/export-policy.md](references/export-policy.md) | `thesis` / `publication` / `communication` 三档分层导出 |
| [references/color_schemes.md](references/color_schemes.md) | 序列/发散/Nature AD2024/Li Lab/NMI Pastel |
| [references/violin-boxplot.md](references/violin-boxplot.md) | 小提琴+箱线叠画（matplotlib 推荐、配色、参数） |
| [references/heatmap-annotation.md](references/heatmap-annotation.md) | 热图列分组注释（GridSpec 分轴，避免底栏叠字） |
| [references/journal_requirements.md](references/journal_requirements.md) | Nature/Cell/Science 尺寸与字体 |
| [references/troubleshooting.md](references/troubleshooting.md) | 标签重叠、截断、colorbar 等 |

---

## 最终检查清单

- [ ] 确认任务属于单图或简单 2–4 panel（非 hero/contract 复杂大组图 → nature-figure）
- [ ] 未主动出图；若建议了出图则已获用户确认
- [ ] 未指定具体图型时，已按 [chart-selection.md](references/chart-selection.md) 匹配高信息密度图型（排名数据已排序、大样本已防过绘、$\ge 4$ 集合用 UpSet）
- [ ] 后端已选定（默认 Python；英文期刊投稿/R 场景已确认）
- [ ] 档位正确：默认走 `thesis`（宽度 $\le 6.20\text{ in}$、扁平 `7.5 pt`、大写 `10 pt` `A/B/C/D`）；提英文期刊走 `publication`；提组会走 `communication`
- [ ] 配色色盲友好；发散热图默认 Nature 紫–绿；UMAP 用定性色（含棕）；violin+box 用 Li Lab
- [ ] 热图有列分组时用 `heatmap_annotation.py` 或独立 axes；勿在热图上叠手绘色条 + `xlabel`
- [ ] 标签无重叠；基因名与统计符号（`*p*`、`*n*`、`*r*`）斜体；所有图内文字与数字 $\le 10.5\text{ pt}$（五号字）
- [ ] 浓度单位统一用 `mol/L`（不用 `M/mM/μM`），数字与单位留空格（`%`、`℃` 除外）；多折线用不同 marker；UMAP/spatial 移除无意义刻度数字
- [ ] 无多余的副标题、说明文字或口号式文案；能靠布局表达的不靠文字
- [ ] `sns.despine()`；轴标签含单位
- [ ] QC 已通过（默认 `scripts/qc.py <fig>.png --mode thesis`）
