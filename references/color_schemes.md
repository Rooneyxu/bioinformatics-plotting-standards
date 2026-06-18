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

用于表示双向变化的数据，如 z-scores、fold-changes、相关系数。

#### RdBu_r（推荐）
- **用途**：差异表达、z-scores、相关性
- **特点**：蓝色（低/负）→ 白色（中性）→ 红色（高/正）
- **代码**：
```python
plt.imshow(data, cmap='RdBu_r', vmin=-3, vmax=3, center=0)
```

#### PuOr
- **用途**：替代 RdBu_r
- **特点**：紫色（低）→ 白色 → 橙色（高）
- **代码**：
```python
plt.imshow(data, cmap='PuOr')
```

#### BrBG
- **用途**：环境数据、生态学数据
- **特点**：棕色（低）→ 白色 → 蓝绿色（高）
- **代码**：
```python
plt.imshow(data, cmap='BrBG')
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

---

## NMI Pastel 分类配色（方法对比 / 多组条形图）

用于**分类变量**（处理组、细胞类型、方法变体），尤其多个相关方法属于同一色系、需要页面视觉统一时。
连续/发散数据仍用 `plasma` / `RdBu_r`，不要用 pastel 替代热图 colormap。

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
| 2–3 组简单对比 | Nature 三色 `#0173B2` / `#DE8F05` / `#029E73` 或 Set2 |
| 4–8 组方法/变体对比 | NMI Pastel |
| 连续表达/强度 | plasma / viridis（不用 pastel） |
| 正负 fold-change | RdBu_r；方向标注用 delta_up / delta_down |

---

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
import matplotlib.pyplot as plt

# 序列数据（表达量）
sns.heatmap(expr_data, cmap='plasma', cbar_kws={'label': 'Expression (log2 TPM)'})

# 发散数据（z-scores）
sns.heatmap(zscore_data, cmap='RdBu_r', center=0, vmin=-3, vmax=3,
            cbar_kws={'label': 'Z-score'})
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

# 按连续值着色
scatter = ax.scatter(x, y, c=values, cmap='viridis', s=50, alpha=0.7)
plt.colorbar(scatter, label='Value')
```

### 小提琴图（Violin Plot）

```python
import seaborn as sns

# 使用柔和配色
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
| 基因表达 | plasma | `cmap='plasma'` |
| 空间转录组 | plasma_r | `cmap='plasma_r'` |
| Z-scores | RdBu_r | `cmap='RdBu_r', center=0` |
| 相关性 | RdBu_r | `cmap='RdBu_r', vmin=-1, vmax=1` |
| 细胞类型 | Set2 | `sns.color_palette("Set2")` |
| 实验条件 | tab10 | `plt.cm.tab10.colors` |

### 配色检查清单

- [ ] 配色方案色盲友好（避免红绿）
- [ ] 通过灰度测试
- [ ] 感知均匀（序列数据）
- [ ] 中心点对齐（发散数据）
- [ ] 颜色含义在图表系列中一致
- [ ] 避免使用 jet/rainbow
- [ ] Colorbar 标签包含单位
- [ ] 配色范围合理（考虑百分位数截断）
