# 配色方案指南

生物信息学图表的配色方案选择和应用指南。

## 核心原则

1. **色盲友好**：避免红绿组合，使用感知均匀的配色
2. **灰度可读**：图表在灰度打印时仍可解读
3. **感知均匀**：颜色变化与数据变化成比例
4. **语义一致**：在同一研究中保持颜色含义一致

---

## 推荐配色方案

### 序列数据（Sequential）

用于表示单向变化的数据，如表达水平、强度、浓度。

#### plasma（推荐）
- **用途**：基因表达、蛋白质丰度、信号强度
- **特点**：黄色（低）→ 紫色（高），感知均匀，色盲友好
- **代码**：
```python
import matplotlib.pyplot as plt
plt.imshow(data, cmap='plasma')
```

#### plasma_r（反向）
- **用途**：空间转录组学、热图（深色背景更突出高值）
- **特点**：深紫色（低）→ 黄色（高）
- **代码**：
```python
plt.imshow(data, cmap='plasma_r')
```

#### viridis
- **用途**：通用序列数据
- **特点**：深蓝（低）→ 黄色（高），matplotlib 默认
- **代码**：
```python
plt.imshow(data, cmap='viridis')
```

#### cividis
- **用途**：需要极致色盲友好的场景
- **特点**：专为色盲设计，蓝色到黄色
- **代码**：
```python
plt.imshow(data, cmap='cividis')
```

---

### 发散数据（Diverging）

用于表示双向变化的数据，如 z-scores、fold-changes、相关系数、表型连续评分。

#### Nature AD2024 紫–绿（**默认推荐**）

- **来源**：Green et al., *Nature* 2024（`lilab_plot_code/配色.pdf`）；Fig.1c 认知下降率、发散热图
- **特点**：负值/低端 **紫** `#7B3294` → 白 → 正值/高端 **绿** `#008837`；比 `RdBu_r` 更贴近 Nature 版面，色盲友好
- **用途**：z-score 热图、相关矩阵、连续表型散点着色、轨迹评分
- **代码**：

```python
from scripts.nature_ad2024_colors import get_diverging_cmap

cmap_pg = get_diverging_cmap()
sns.heatmap(zscore_data, cmap=cmap_pg, center=0, vmin=-3, vmax=3,
            cbar_kws={"label": "Z-score"})
# 散点连续着色
ax.scatter(x, y, c=values, cmap=cmap_pg, vmin=-0.3, vmax=0.1)
```

#### RdBu_r（传统红蓝语义）

- **用途**：需明确 **红=上调/正、蓝=下调/负** 的火山图、fold-change 热图（读者习惯红蓝时保留）
- **特点**：蓝色（低/负）→ 白色 → 红色（高/正）
- **代码**：

```python
plt.imshow(data, cmap="RdBu_r", vmin=-3, vmax=3)
```

#### PuOr / BrBG

- **PuOr**：紫–橙发散，RdBu_r 与 Nature 紫绿之间的折中
- **BrBG**：**棕**–白–蓝绿发散；低端棕色可与 `NATURE_BROWN_TERRACOTTA` 呼应

```python
plt.imshow(data, cmap="BrBG", center=0)
```

---

### 分类数据（Qualitative）

用于区分不同类别，如细胞类型、实验条件、样本组。

#### tab10（matplotlib 默认）
- **用途**：最多 10 个类别
- **颜色**：蓝、橙、绿、红、紫、棕、粉、灰、黄绿、青
- **代码**：
```python
colors = plt.cm.tab10.colors
ax.scatter(x, y, c=[colors[i] for i in categories])
```

#### Set2（推荐用于生物学）
- **用途**：柔和的分类配色，适合出版物
- **特点**：8 种柔和颜色，视觉舒适
- **代码**：
```python
import seaborn as sns
palette = sns.color_palette("Set2")
```

#### 自定义 Nature 风格配色
```python
nature_colors = {
    'blue': '#0173B2',
    'orange': '#DE8F05',
    'green': '#029E73',
    'red': '#CC3311',
    'purple': '#9C27B0',
    'brown': '#8D6E63',
    'pink': '#EC407A',
    'grey': '#78909C'
}
```

#### Nature AD2024 多类别（UMAP / 细胞亚群，**含棕色**）

用于 scanpy UMAP、dotplot 多 cluster、图例 ≥4 类；**优先于 tab10**。棕色 `#8C564B` 适合小胶质/髓系等亚群（Mic.12/13 赤褐）。

```python
from scripts.nature_ad2024_colors import QUALITATIVE_NATURE_AD2024, qualitative_palette

palette = qualitative_palette(df["cluster"].nunique())
# scanpy
adata.uns["cluster_colors"] = palette[: adata.obs["cluster"].nunique()]
sc.pl.umap(adata, color="cluster", palette=palette)
```

| 角色 | Hex | 备注 |
|------|-----|------|
| 深紫 | `#762A83` | Mic.7 |
| 森林绿 | `#008837` | Mic.9 |
| **赤褐** | `#8C564B` | **Mic.12/13，主推棕色** |
| 海军蓝 | `#016FAF` | Mic.1/16 |
| 鼠尾草绿 | `#5AAE61` | Mic.3–5 |
| 薰衣草 | `#C2A5CF` | Mic.6/10/11 |
| 金棕 | `#BF812D` | 强调色 |
| 褐紫 | `#9970AB` | Mic.15 |

完整列表见 `scripts/nature_ad2024_colors.py` 中 `QUALITATIVE_NATURE_AD2024`。

---

## NMI Pastel 分类配色（方法对比 / 多组条形图）

用于**分类变量**（处理组、细胞类型、方法变体），尤其多个相关方法属于同一色系、需要页面视觉统一时。
连续/发散数据仍用 `plasma` 或 **Nature 紫–绿** / `RdBu_r`，不要用 pastel 替代热图 colormap。

**原则**（借鉴 nature-figure）：

- **方法族一致性**优先于最大色相分离——同一 figure 内条件/方法颜色保持一致。
- 绿/红仅用于**方向性**提示（上调/下调、增益/下降），不要滥作普通分类色。
- 低饱和度，适合密集 bar/violin/dotplot。

### Python 常量

```python
PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "neutral_light": "#D8D8D8",
    "neutral_mid":   "#A8A8A8",
    "neutral_dark":  "#606060",
    "delta_up":   "#2E9E44",   # 上调 / 增益
    "delta_down": "#E53935",   # 下调 / 下降
}

DEFAULT_COLORS_NMI_PASTEL = [
    PALETTE_NMI_PASTEL["baseline_dark"],
    PALETTE_NMI_PASTEL["baseline_mid"],
    PALETTE_NMI_PASTEL["baseline_soft"],
    PALETTE_NMI_PASTEL["ours_tiny"],
    PALETTE_NMI_PASTEL["ours_base"],
    PALETTE_NMI_PASTEL["ours_large"],
]
```

### 使用示例

```python
import seaborn as sns

palette = DEFAULT_COLORS_NMI_PASTEL[:df["group"].nunique()]
sns.barplot(data=df, x="gene", y="expression", hue="group", palette=palette)
```

### R 等效

```r
nmi_pastel <- c(
  "#484878", "#7884B4", "#B4C0E4",
  "#E4E4F0", "#E4CCD8", "#F0C0CC"
)
ggplot(df, aes(x = gene, y = expression, fill = group)) +
  geom_col(position = "dodge") +
  scale_fill_manual(values = nmi_pastel)
```

### 何时用哪套分类色

| 场景 | 推荐 |
|---|---|
| 2–3 组简单对比 | Nature 三色或 Li Lab triple |
| **小提琴+箱线叠画（Li Lab）** | pair / triple；见 [violin-boxplot.md](violin-boxplot.md) |
| 4–8 组方法/变体对比 | NMI Pastel |
| **UMAP / 多细胞亚群（含棕）** | **Nature AD2024 定性色** `qualitative_palette()` |
| 连续表达/强度 | plasma / viridis；**分类计数条**用顺序紫 `NATURE_SEQ_PURPLE` |
| z-score / 相关 / 连续表型 | **Nature 紫–绿发散**（默认）；`RdBu_r` 仅当红蓝语义必要 |
| 火山 fold-change 热图 | `RdBu_r` 或 Nature 紫–绿（与全文统一即可） |

---

## Nature AD2024 配色（Green et al., 2024）

参考 `lilab_plot_code/配色.pdf` 与 `oyj/供参考的配色*.pptx`。与 **Li Lab violin 分类色**分工：Li Lab 管 2–3 组统计图；本节管 **连续发散、多 cluster、棕色亚群**。

### 发散紫–绿（替代默认 RdBu_r 的首选）

| 端点 | Hex |
|------|-----|
| 负/低 | `#7B3294` |
| 零 | `#FFFFFF` |
| 正/高 | `#008837` |

```python
from scripts.nature_ad2024_colors import get_diverging_cmap
cmap = get_diverging_cmap()
```

### 顺序紫（Fig.1b 条形图 / 单变量等级）

`#E7D4E8` → `#C2A5CF` → `#A17CB4` → `#8B5A9F` → `#762A83`

```python
from scripts.nature_ad2024_colors import NATURE_SEQ_PURPLE, get_sequential_purple_cmap

ax.bar(x, height, color=NATURE_SEQ_PURPLE[: len(x)])
# 或连续色带
sns.heatmap(data, cmap=get_sequential_purple_cmap())
```

### 棕色系（UMAP 小胶质等）

| 名称 | Hex | 用途 |
|------|-----|------|
| 赤褐 | `#8C564B` | Mic.12/13，**默认棕** |
| 金棕 | `#BF812D` | 强调、第三分类 |
| 浅褐 | `#C49C94` | 填充、次要 |
| 褐紫 | `#9970AB` | Mic.15 |

```python
from scripts.nature_ad2024_colors import NATURE_BROWN_TERRACOTTA, NATURE_BROWN_GOLD
```

### 何时仍用 RdBu_r / plasma

- **RdBu_r**：审稿人/合作者明确要求红=上调、蓝=下调
- **plasma / viridis**：非对称、仅正值的连续强度（表达量、count）

---

## Li Lab violin+box 叠画配色

用于**小提琴 + 箱线图同轴叠画**（分布 + 四分位）。源自实验室 `lilab_plot_code`；与 NMI Pastel 互补——Li Lab 偏紫/橙/灰低饱和，适合 2–3 组表达/打分对比。

### pair（两组交替，成对并排）

| 角色 | 色 1（主/紫） | 色 2（对照/灰） |
|------|---------------|-----------------|
| 小提琴填充 | `#DDC4E0` | `#E9E9E9` |
| 箱线边框/须/中位数/离群点 | `#A362AC` | `#BEBEBE` |
| 箱内填充 | `#FFFFFF` | `#FFFFFF` |
| 水平参考线（可选） | `#7F7F7F`（alpha=0.5） | |

### triple（三组分类轴）

| 角色 | 组 1 | 组 2 | 组 3 |
|------|------|------|------|
| 小提琴填充 | `#DDC4E0` | `#FFD4AB` | `#E9E9E9` |
| 箱线边框/须/中位数 | `#984EA3` | `#FF7F00` | `#BEBEBE` |
| 箱内填充 | `#F1E6F2` | `#FAE9D8` | `#F6F6F6` |

### Python 常量与调用

```python
from scripts.violin_boxplot import (
    PALETTE_LILAB_PAIR,
    PALETTE_LILAB_TRIPLE,
    plot_violin_box,
    plot_violin_box_grouped,
)

# 三组长表
fig, ax = plot_violin_box_grouped(df, x="Group", y="score", palette="triple")

# 成对自定义 positions
fig, ax = plot_violin_box(data_list, positions, palette="pair", color_indices=[0,1,0,1])
```

完整参数与 seaborn 对比见 [violin-boxplot.md](violin-boxplot.md)。


### ❌ jet / rainbow
- **问题**：感知不均匀，色盲不友好，在灰度下失去信息
- **替代**：使用 `viridis` 或 `plasma`

### ❌ 红绿组合
- **问题**：红绿色盲（8% 男性）无法区分
- **替代**：使用蓝橙、蓝黄、紫橙组合

### ❌ 过于鲜艳的颜色
- **问题**：视觉疲劳，不专业
- **替代**：使用柔和的 Set2 或自定义柔和配色

---

## 配色应用示例

### 热图（Heatmap）

```python
import seaborn as sns
from scripts.nature_ad2024_colors import get_diverging_cmap, get_sequential_purple_cmap

cmap_pg = get_diverging_cmap()

# 序列数据（表达量）— 仍用 plasma
sns.heatmap(expr_data, cmap="plasma", cbar_kws={"label": "Expression (log2 TPM)"})

# 发散数据（z-scores）— 默认 Nature 紫–绿
sns.heatmap(zscore_data, cmap=cmap_pg, center=0, vmin=-3, vmax=3,
            cbar_kws={"label": "Z-score"})

# fold-change 若需红蓝语义
sns.heatmap(fc_data, cmap="RdBu_r", center=0, vmin=-3, vmax=3)
```

### 散点图（Scatter Plot）

```python
# 按类别着色
categories = ['Type A', 'Type B', 'Type C']
colors = sns.color_palette("Set2", n_colors=len(categories))
for i, cat in enumerate(categories):
    mask = data['category'] == cat
    ax.scatter(data.loc[mask, 'x'], data.loc[mask, 'y'],
               c=[colors[i]], label=cat, s=50, alpha=0.7)
ax.legend()

# 按连续值着色 — Nature 紫–绿或 plasma
from scripts.nature_ad2024_colors import get_diverging_cmap
scatter = ax.scatter(x, y, c=values, cmap=get_diverging_cmap(), s=50, alpha=0.7)
plt.colorbar(scatter, label="Score")
```

### 小提琴图（Violin Plot）

- **小提琴 + 箱线叠画**（Li Lab 风格，推荐）：见 [violin-boxplot.md](references/violin-boxplot.md)，脚本 `scripts/violin_boxplot.py`，配色 `pair` / `triple`。
- **纯小提琴**（无箱线）：

```python
import seaborn as sns

palette = sns.color_palette("Set2")
sns.violinplot(data=df, x='condition', y='expression', palette=palette)
```

### 空间转录组学

```python
# 使用 plasma_r 使高表达区域更突出
import scanpy as sc

sc.pl.spatial(adata, color='gene_name', cmap='plasma_r',
              vmin=0, vmax='p99', size=1.5)
```

---

## 高级技巧

### 自定义离散配色

```python
from matplotlib.colors import ListedColormap

# 创建自定义配色
custom_colors = ['#E8F4F8', '#B3D9E8', '#7FBFD8', '#4BA4C8', '#1789B8']
custom_cmap = ListedColormap(custom_colors)

plt.imshow(data, cmap=custom_cmap)
```

### 归一化配色范围

```python
from matplotlib.colors import TwoSlopeNorm

# 发散配色，中心点为 0
norm = TwoSlopeNorm(vmin=-5, vcenter=0, vmax=10)
plt.imshow(data, cmap='RdBu_r', norm=norm)
```

### 对数尺度配色

```python
from matplotlib.colors import LogNorm

# 用于跨数量级的数据
plt.imshow(data, cmap='viridis', norm=LogNorm(vmin=1, vmax=1000))
```

### 百分位数截断

```python
import numpy as np

# 避免极端值影响配色
vmin, vmax = np.percentile(data, [1, 99])
plt.imshow(data, cmap='plasma', vmin=vmin, vmax=vmax)
```

---

## 配色测试

### 色盲模拟测试

使用在线工具测试配色：
- **Coblis**：https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Viz Palette**：https://projects.susielu.com/viz-palette

### 灰度转换测试

```python
# 将图表转换为灰度查看
from PIL import Image
import numpy as np

# 保存彩色图
fig.savefig('color.png', dpi=300)

# 转换为灰度
img = Image.open('color.png').convert('L')
img.save('grayscale.png')
```

### Python 色盲模拟

```python
# 使用 colorspacious 库模拟色盲视觉
from colorspacious import cspace_convert

def simulate_colorblind(rgb, cvd_type='deuteranomaly'):
    """
    cvd_type: 'protanomaly', 'deuteranomaly', 'tritanomaly'
    """
    from colorspacious import cspace_convert
    # 实现色盲模拟
    pass
```

---

## 期刊特定配色建议

### Nature 系列
- **首选**：蓝色系（#0173B2）作为主色
- **辅助**：橙色（#DE8F05）、绿色（#029E73）
- **避免**：过于鲜艳的颜色

### Cell 系列
- **首选**：柔和的 Set2 配色
- **热图**：plasma 或 viridis
- **发散**：RdBu_r

### Science
- **首选**：蓝橙组合（色盲友好）
- **避免**：红绿组合
- **强调**：使用高对比度但不刺眼的颜色

---

## 快速参考

### 常用配色速查

| 数据类型 | 推荐配色 | 代码 |
|---------|---------|------|
| 基因表达（仅正值） | plasma | `cmap='plasma'` |
| 空间转录组 | plasma_r | `cmap='plasma_r'` |
| Z-scores / 相关 | **Nature 紫–绿** | `get_diverging_cmap()` |
| Fold-change（红蓝语义） | RdBu_r | `cmap='RdBu_r', center=0` |
| UMAP / 多 cluster | Nature AD2024 定性 | `qualitative_palette(n)` |
| 分类计数条 | 顺序紫 | `NATURE_SEQ_PURPLE` |
| 细胞类型（柔和） | Set2 | `sns.color_palette("Set2")` |
| 小提琴+箱线 | Li Lab pair/triple | `violin_boxplot.py` |

### 配色检查清单

- [ ] 配色方案色盲友好（避免红绿）
- [ ] 通过灰度测试
- [ ] 感知均匀（序列数据）
- [ ] 中心点对齐（发散数据）
- [ ] 颜色含义在图表系列中一致
- [ ] 避免使用 jet/rainbow
- [ ] Colorbar 标签包含单位
- [ ] 配色范围合理（考虑百分位数截断）
