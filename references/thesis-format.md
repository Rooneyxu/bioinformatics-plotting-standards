# 北京大学学位论文图表与表格字号画布规范（Thesis Format）

本规范针对学位论文排版（当前近期默认启用），同时完全保留原有的英文期刊 `publication` 档与日常沟通 `communication` 档。

---

## 一、核心红线与版面物理锚点

1. **字号红线**：全论文所有**图内与表内**的文字、数字物理字号必须 **$\le$ 五号字（`10.5 pt`）**，且尽可能全文统一。
2. **画布最大宽度上限 $\le 6.20\text{ in}$ (`15.75 cm` / `446 pt`)**：
   - 标准 A4 竖排纸宽 `21.00 cm`，左右页边距各 `2.60 cm` $\rightarrow$ **正文版心净宽 `15.80 cm`（`6.22 in` / `447.9 pt`）**。
   - **宽度随内容自由设定**：只要导出的图片总宽 **$\le 6.20\text{ in}$ (`15.75 cm`)**，并且**以 100% 原始尺寸插入 Word / LaTeX（不在 Word 里手动拖拽缩放）**，无论该图宽 `3.2 in`、`4.5 in` 还是 `6.2 in`，印在纸上的 `7.5 pt` 与 `10 pt` 字号都 100% 物理一致。
   - `scripts/thesis_style.py` 既支持直接传入任意 `width_in`，也提供三个常用参考预设（非强制锁死）：`full = 6.20 in (15.75 cm)`、`medium = 4.20 in (10.67 cm)`、`half = 3.00 in (7.62 cm)`。若专门用于横向页（Landscape）超出 `6.22 in`，`qc.py` 仅输出 `[WARN]` 提醒而不硬阻断。

---

## 二、扁平 7.5 pt 统一字号体系（Flat 7.5 pt Hierarchy）

为了消除不同图之间坐标轴、刻度、图例与注释字号的视觉参差，学位论文模式采用**极简扁平三层字号**，图内语言**以英文为主**（Word 图注自行写中文），字体统一为 **`Arial`**（偶含中文字符时自动回退 `SimHei` / `Noto Sans CJK`）：

| 元素层级 | 字号 (`pt`) | 中文字号对照 | 字体与字重 | 一致性硬约束 |
|---|---|---|---|---|
| **组图面板字母（`A, B, C, D`）** | **`10.0 pt`** | 略小于五号 (`10.5 pt`) | `Arial Bold`（**必须大写**） | 全文所有组图的 A/B/C/D 字体、字号、加粗必须 **100% 一致**；单图不标 `A` |
| **子图标题（Panel Title）** | **`8.5 pt`** | 略小于小五 (`9.0 pt`) | `Arial Bold` | 仅在确需区分模块/子集时添加；若图注已说明可省略 |
| **常规图内文字（全员统一）** | **`7.5 pt`** | **六号字** | `Arial Regular`（基因名与统计符号斜体） | **坐标轴标题、刻度数字、图例文字、*p* 值、相关系数、常规标注统一为 `7.5 pt`** |
| *超密标注特例* | *`6.5 pt`* | *略小于六号* | *`Arial Regular/Italic`* | *仅当火山图/热图 >10 个基因或点标签拥挤时降为 `6.5 pt`（硬下限 `6.0 pt`）* |

### 细节格式硬规范（来自北大医学部学位论文模板与形式审查要点）

1. **统计学符号必须斜体**：图内显著性与统计量符号（`*p*`、`*n*`、`*r*`、`*t*`）统一用**斜体**（Matplotlib 用 `r"$\it{p}$ = 2.4e-9"` 或 `format_stat_p()`，R 用 `italic(p)`），严禁写成正体 `P =`。
2. **浓度单位与数字空格规范**：
   - 摩尔浓度统一用 **`mol/L`**（如 `mmol/L`、`μmol/L`、`nmol/L`），**不得用 `M`（如 `mM`、`μM`）**；
   - 数字与单位之间**必须留一个半角空格**（如 `3 mol/L`、`5 mL`、`10 μm`、`50 s`），**`%` 和 `℃` 除外**（紧贴数字如 `50%`、`37℃`）。
3. **多条曲线点型区分**：同一坐标系内绘制多条折线/曲线时，不能仅靠颜色区分，必须同时使用**不同形状的标识符（marker，如 `THESIS_MARKERS = ["o", "s", "^", "D", "v", "P"]`）**或线型区分，确保黑白打印/缩微清晰可辨。
4. **无物理意义坐标轴去掉数字**：UMAP / t-SNE / 组织空间原位切片等横纵坐标具体数值无物理意义的图，直接移除刻度数字与刻度线（`strip_meaningless_ticks(ax)` 或左下角简短方向箭头），避免留下细小无意义数字。

### 配套论文表格与图题备忘（Word / LaTeX 侧）

- **图题（位于图下方居中）& 表题（位于表上方居中）**：**必须是中文**，字号 **五号字（`10.5 pt`，Word XML `w:sz=21`）**，中文宋体 + 英文/数字 Times New Roman（切勿误设为 `11 pt`；图序按章编号如 `图 4.1  标题`，中间空一格，序号后不加英文句点 `.`）。
- **三线表表头与单元格**：表头必须是中文；表内文字与数字统一使用 **小五号（`9.0 pt`）** 或 **六号（`7.5 pt`）**（全文表格选定一档保持一致，严禁超过五号 `10.5 pt`；跨页表须写 `续表 X.X` 并重复表头）。

---

## 三、Python 与 R 标准调用模板

### Python（优先直接调用 `scripts/thesis_style.py`）

```python
from scripts.thesis_style import (
    THESIS_FONT_SIZES,
    create_thesis_figure,
    add_panel_labels,
    save_thesis_figure,
)
import seaborn as sns

# 1. 创建固定 6.20 in 通栏 1x2 组图（自动应用 Arial + 8.5pt 标题 + 全员 7.5pt 六号字）
fig, axes = create_thesis_figure(width_tier="full", height_in=2.7, nrows=1, ncols=2)

for ax in axes:
    # ... 绘图逻辑（注释统一使用 fontsize=THESIS_FONT_SIZES["body"] 即 7.5 pt）...
    sns.despine(ax=ax)

# 2. 统一打上 10.0 pt Arial Bold 大写 A, B（自动对齐同行高度）
add_panel_labels(fig, axes)  # 默认生成 ["A", "B", ...]

# 3. 导出 600 DPI PNG + 可编辑 PDF + SVG（总宽 <= 6.20 in，100% 原大插入 Word 即可）
save_thesis_figure(fig, "figures/fig_4_1")
```

### R（`ggplot2` + `patchwork`）

```r
library(ggplot2)
library(patchwork)

theme_thesis <- function() {
  theme_classic(base_size = 7.5, base_family = "Arial") +
    theme(
      plot.title = element_text(size = 8.5, face = "bold", hjust = 0.5),
      axis.title = element_text(size = 7.5, face = "plain", colour = "black"),
      axis.text = element_text(size = 7.5, colour = "black"),
      legend.title = element_text(size = 7.5, face = "plain"),
      legend.text = element_text(size = 7.5),
      legend.background = element_blank(),
      axis.line = element_line(linewidth = 0.35, colour = "black"),
      axis.ticks = element_line(linewidth = 0.35, colour = "black")
    )
}

# 组图拼接：统一使用大写 A, B, C, D (10 pt Arial Bold)
p_comb <- (p1 | p2) +
  plot_annotation(tag_levels = "A") &
  theme_thesis() &
  theme(plot.tag = element_text(size = 10, face = "bold", family = "Arial"))

# 通栏固定 6.20 in (单图居中用 4.20 in，半栏用 3.00 in)
ggsave("figures/fig_4_1.png", p_comb, width = 6.20, height = 2.70, units = "in", dpi = 600)
ggsave("figures/fig_4_1.pdf", p_comb, width = 6.20, height = 2.70, units = "in", device = cairo_pdf)
ggsave("figures/fig_4_1.svg", p_comb, width = 6.20, height = 2.70, units = "in")
```

---

## 四、自动质检（必跑）

保存后运行 `thesis` 模式质检，自动扫描 DPI、物理宽度（$\le 6.22\text{ in}$）、PDF 全部字形上限（$\le 10.5\text{ pt}$）以及大写 `A/B/C/D` 字体字号一致性：

```bash
python scripts/qc.py figures/fig_4_1.png --mode thesis
```
