# 小提琴图 + 箱线图叠画（Li Lab 风格）

在同一坐标轴上先画**小提琴**（分布形态），再叠**箱线**（四分位与离群点）。配色来自实验室 `lilab_plot_code`（`violin_boxplot.py`、`dhq_plot.ipynb`）。

---

## 实现选型：推荐 matplotlib，seaborn 仅作备选

| 维度 | **matplotlib**（推荐） | seaborn 双层叠画 |
|------|------------------------|------------------|
| 位置对齐 | `violinplot` + `boxplot` 共用 `positions`，精确 | `width`/`cut` 不当易错位 |
| 成对并排 | 支持非等距 `positions`（如 PS/NPS 各贴一侧） | 需 hack `x` 偏移 |
| 配色控制 | 按 index 循环，逻辑清晰 | 须改 `collections`/`lines`，须线索引脆弱 |
| 紧凑投稿图 | 已验证 `figsize=(2.5, 1)` + 600 dpi | 默认 fig 偏大 |
| DataFrame API | 用 `plot_violin_box_grouped()` 封装 | 原生 `x`/`y` 列直观 |

**结论**：本 skill **默认用 `scripts/violin_boxplot.py`（matplotlib）**。仅当用户已有 seaborn 脚本且不愿迁移时，可保留旧写法，但须手动核对对齐。

---

## 配色

详见 [color_schemes.md](color_schemes.md)「Li Lab violin+box 叠画配色」。两套：

| 场景 | palette 名 | 小提琴 | 箱线边框 | 箱内 |
|------|------------|--------|----------|------|
| 两组交替（成对比较） | `pair` | `#DDC4E0` / `#E9E9E9` | `#A362AC` / `#BEBEBE` | 白 |
| 三组分类 | `triple` | `#DDC4E0` / `#FFD4AB` / `#E9E9E9` | `#984EA3` / `#FF7F00` / `#BEBEBE` | `#F1E6F2` / `#FAE9D8` / `#F6F6F6` |

可选水平参考线：`#7F7F7F`，`alpha=0.5`，`linewidth=0.1`。

---

## 标准工作流

### 0. 环境（与 SKILL.md 一致）

```python
import matplotlib.pyplot as plt

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["font.family"] = "Arial"
```

### 1. 三组分类（长表 DataFrame）

```python
from scripts.violin_boxplot import plot_violin_box_grouped

fig, ax = plot_violin_box_grouped(
    df, x="Group", y="Predict_score",
    order=["Control", "Treatment A", "Treatment B"],
    palette="triple",
)
# 导出见 export-policy.md
```

### 2. 成对并排（自定义 positions）

用于每个条件下两列数据并排（如 positive vs negative）：

```python
from scripts.violin_boxplot import plot_violin_box

# 每组两个子分布，positions 非等距
data_list = [ps_vals, nps_vals, ps_vals2, nps_vals2, ...]
positions = [i + 2 for i in [-0.5, 0.5, 2.5, 3.5, 5.5, 6.5]]

fig, ax = plot_violin_box(
    data_list,
    positions,
    palette="pair",
    color_indices=[0, 1, 0, 1, 0, 1],
    ref_lines=[0, 5, 10],
    violin_width=1.0,
    show_caps=False,
    ylabel="log2 expression (a.u.)",
)
ax.set_xticks([2, 5, 8])
ax.set_xticklabels(["Cond1", "Cond2", "Cond3"])
```

### 3. 小提琴与箱线参数（与 lab 一致）

| 元素 | 推荐 |
|------|------|
| 小提琴 `bw_method` | `"silverman"` |
| 小提琴 | `showmeans/showmedians/showextrema=False`；`edgecolor=None` |
| 箱线 | `patch_artist=True`；`showcaps=False`（lab 默认） |
| 离群点 | `markersize=0.3`（紧凑图）或 `2`（演示级） |
| 须/中位数线宽 | 0.75 / 1.5 |

### 4. 统计标注

p 值文本放在数据上方空白处，`fontsize=4–5`（紧凑图）或 `6–7`（标准单图）：

```python
ax.text(x, y, "p=1.2e-8", ha="center", fontsize=5)
```

### 5. 导出与 QC

按 [export-policy.md](export-policy.md) 选档；紧凑投稿图常用 **publication**（600 dpi）。

```bash
python scripts/qc.py figure.png --mode publication
```

---

## 与纯 violin / 纯 box 的选择

| 用户需求 | 做法 |
|----------|------|
| 既要分布形态又要四分位 | **本页叠画** |
| 仅看分布、组多且密 | 单独 `sns.violinplot`，无箱线 |
| 仅看四分位、要极简 | 单独 `sns.boxplot` |
| 单细胞 marker 表达 | 常单独 violin；多基因 panel 见 SKILL 简单 multipanel |

---

## 内置 demo

```bash
python scripts/violin_boxplot.py --demo grouped --output /tmp/lilab_violin_box.png
python scripts/violin_boxplot.py --demo paired --output /tmp/lilab_violin_box_paired.png
```

---

## seaborn 旧写法（不推荐，仅兼容）

实验室 `dhq_plot.ipynb` 中的叠画方式：

```python
sns.violinplot(..., inner=None, linewidth=0, color="None", cut=0, width=0.3)
sns.boxplot(..., width=0.08, boxprops={"facecolor": "None"}, ...)
# 再循环 patches/lines 改色 — 须线索引随 seaborn 版本易变
```

新图请改用 `scripts/violin_boxplot.py`。
