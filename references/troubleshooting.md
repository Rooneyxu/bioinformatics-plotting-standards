# 常见布局问题和解决方案

绘图过程中常见的布局问题及其解决方法。

## 目录

1. [文字标签重叠问题](#文字标签重叠问题)
2. [元素重叠问题](#元素重叠问题)
3. [X 轴标签被截断](#x-轴标签被截断)
4. [Colorbar 位置问题](#colorbar-位置问题)
5. [紧密间距导致重叠](#紧密间距导致重叠)
6. [点大小缩放问题](#点大小缩放问题)
7. [字体渲染问题](#字体渲染问题)
8. [多面板对齐问题](#多面板对齐问题)

---

## 文字标签重叠问题

### 症状
- 火山图基因标注互相遮挡
- 散点图关键点标签堆叠
- 标签覆盖了数据点

### Python：adjustText 调参指南

```python
from adjustText import adjust_text

# 基础用法
texts = [ax.text(x, y, label, fontsize=6) for x, y, label in annotations]
adjust_text(texts, ax=ax,
            arrowprops=dict(arrowstyle='-', color='grey', lw=0.5))
```

**常见问题及解决：**

**标签仍然重叠** → 增大排斥力和迭代次数
```python
adjust_text(texts, ax=ax,
            force_text=(1.0, 1.5),     # 增大文本间排斥力（默认 0.5, 0.5）
            force_points=(0.5, 1.0),   # 增大点排斥力
            expand=(1.5, 2.0),         # 增大标签缓冲区
            lim=1000)                  # 增大迭代次数
```

**标签飞得太远** → 减小排斥力，增大拉回力
```python
adjust_text(texts, ax=ax,
            force_text=(0.2, 0.3),     # 减小排斥力
            force_points=(0.1, 0.2),
            expand=(1.05, 1.1))        # 减小缓冲区
```

**只允许标签水平/垂直移动** → 限制移动方向
```python
adjust_text(texts, ax=ax,
            only_move={'text': 'x'})   # 只水平移动
```

**连接线太显眼** → 调整线条样式
```python
adjust_text(texts, ax=ax,
            arrowprops=dict(
                arrowstyle='-',         # 简单线段（不是箭头）
                color='grey',
                lw=0.3,                 # 极细线
                alpha=0.6               # 半透明
            ))
```

### R：ggrepel 调参指南

```r
# 基础用法
geom_text_repel(aes(label = gene_name), size = 2)
```

**常见问题及解决：**

**"Too many overlaps" 警告** → 增大 max.overlaps
```r
geom_text_repel(aes(label = gene_name),
                max.overlaps = Inf)     # 不限制（可能很慢）
```

**标签位置不理想** → 调整力和间距
```r
geom_text_repel(aes(label = gene_name),
                force = 5,              # 增大排斥力（默认 1）
                force_pull = 0.1,       # 减小拉回力
                box.padding = 0.5,      # 增大标签间距
                point.padding = 0.3)
```

**只显示部分标签** → 使用 geom_label_repel 并筛选数据
```r
geom_text_repel(
    data = subset(df, padj < 0.01),    # 只标注最显著的
    aes(label = gene_name),
    max.overlaps = 20)
```

---

## 元素重叠问题

### 症状
- 图例与 colorbar 重叠
- 标签与数据点重叠
- 注释过于拥挤

### 解决方案

**方案 1: 轻微增加图表尺寸**
```python
fig, ax = plt.subplots(figsize=(3.5, 4.2))  # 从 (3, 4) 增加
```

**方案 2: 使用显式定位**
```python
# 将图例放置在图表外部右侧
ax.legend(bbox_to_anchor=(1.28, 0.2), loc='center left', frameon=False)
```

**方案 3: 使用 GridSpec 分配专用空间**
```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(4, 4))
gs = GridSpec(1, 2, width_ratios=[4, 0.2], wspace=0.05)

ax_main = fig.add_subplot(gs[0])
ax_cbar = fig.add_subplot(gs[1])
```

**方案 4: 调整 constrained_layout 参数**
```python
fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.02, wspace=0.03, hspace=0.02)
```

---

## X 轴标签被截断

### 症状
旋转的 X 轴标签延伸到图表边界之外，在导出的图片中被截断。

### 解决方案

**方案 1: 使用正确的对齐方式**
```python
plt.setp(ax.get_xticklabels(), rotation=45, ha="center", va="top")
ax.tick_params(axis="x", which="major", pad=3)
```

**方案 2: 添加底部边距**
```python
fig.subplots_adjust(bottom=0.15)  # 增加底部空间
```

**方案 3: 使用 tight_layout 的 rect 参数**
```python
fig.tight_layout(rect=[0, 0.05, 1, 1])  # 底部留 5% 空间
```

**方案 4: 在保存时使用 bbox_inches**
```python
fig.savefig("output.png", dpi=600, bbox_inches="tight")  # 自动裁剪
```

---

## Colorbar 位置问题

### 症状
Colorbar 与主图之间有过多的空白，或者 colorbar 太远。

### 解决方案

**方案 1: 调整右边距**
```python
fig.subplots_adjust(right=0.88)  # 减少右侧空间
```

**方案 2: 手动调整 colorbar 位置**
```python
# 获取 colorbar 的 axes（通常是最后一个）
cbar_ax = fig.axes[-1]
pos = cbar_ax.get_position()

# 向左移动 colorbar
cbar_ax.set_position([pos.x0 - 0.02, pos.y0, pos.width, pos.height])
```

**方案 3: 使用 GridSpec 精确控制**
```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(4, 4))
gs = GridSpec(1, 2, width_ratios=[1, 0.05], wspace=0.05)

ax_main = fig.add_subplot(gs[0])
ax_cbar = fig.add_subplot(gs[1])

# 绘制主图
im = ax_main.imshow(data, cmap='plasma')

# 添加 colorbar
plt.colorbar(im, cax=ax_cbar)
```

**方案 4: 使用 make_axes_locatable**
```python
from mpl_toolkits.axes_grid1 import make_axes_locatable

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(im, cax=cax)
```

---

## 紧密间距导致重叠

### 症状
相邻元素接触或重叠，特别是在使用非常小的间距值时。

### 解决方案

**方案 1: 适度增加间距**
```python
# 从过小的值增加
fig.set_constrained_layout_pads(wspace=0.03, hspace=0.03)  # 而不是 0.01
```

**方案 2: 按比例减小元素尺寸**
```python
# 减小字体大小
ax.tick_params(labelsize=6)  # 从 7 减小到 6
ax.set_xlabel("Label", fontsize=7)  # 从 8 减小到 7
```

**方案 3: 增加图表尺寸**
```python
# 如果内容密度太高，增加整体尺寸
fig, ax = plt.subplots(figsize=(4, 5))  # 从 (3, 4) 增加
```

---

## 点大小缩放问题

### 症状
散点图或 dotplot 中的点太大或太小，视觉比例不合理。

### 解决方案

**使用平方根缩放实现感知平衡**
```python
# 对于 dotplot（大小表示百分比）
sizes = (pct_mat / 100.0) ** 0.5 * scale_factor

# 典型的 scale_factor 值：
# - 紧凑图表 (3-4 inches): 200-300
# - 中等图表 (5-7 inches): 400-500
# - 大型图表 (>7 inches): 600-900
```

**示例：调整散点图点大小**
```python
import numpy as np

# 原始数据（例如表达百分比）
percentages = np.array([10, 25, 50, 75, 100])

# 应用平方根缩放
sizes = (percentages / 100.0) ** 0.5 * 250

# 绘制
ax.scatter(x, y, s=sizes, c=colors, alpha=0.8)
```

---

## 字体渲染问题

### 症状
导出的 PDF/SVG 中字体显示为轮廓或无法编辑，或者字体不一致。

### 解决方案

**在创建任何图表之前设置字体配置**
```python
import matplotlib.pyplot as plt

# 必需：正确的字体嵌入设置
plt.rcParams['svg.fonttype'] = 'none'  # SVG 中保留文本
plt.rcParams['pdf.fonttype'] = 42      # PDF 中使用 TrueType 字体
plt.rcParams['font.family'] = 'Arial'  # 使用 Arial 字体
```

**验证字体是否可用**
```python
import matplotlib.font_manager as fm

# 列出所有可用字体
available_fonts = [f.name for f in fm.fontManager.ttflist]
print('Arial' in available_fonts)  # 应该返回 True
```

**如果 Arial 不可用，使用替代方案**
```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
```

---

## 多面板对齐问题

### 症状
多面板图表中的子图对齐不一致，轴标签位置不统一。

### 解决方案

**方案 1: 使用 constrained_layout**
```python
fig, axes = plt.subplots(2, 3, figsize=(9, 6), constrained_layout=True)
fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.02, wspace=0.03, hspace=0.03)
```

**方案 2: 使用 GridSpec 精确控制**
```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(9, 6))
gs = GridSpec(2, 3, figure=fig, wspace=0.3, hspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
# ... 等等
```

**方案 3: 统一轴范围和刻度**
```python
# 对所有子图使用相同的 y 轴范围
y_min, y_max = 0, 100
for ax in axes.flat:
    ax.set_ylim(y_min, y_max)
    ax.set_yticks([0, 25, 50, 75, 100])
```

**方案 4: 对齐轴标签**
```python
# 确保所有子图的轴标签对齐
fig.align_ylabels(axes[:, 0])  # 对齐第一列的 y 标签
fig.align_xlabels(axes[-1, :])  # 对齐最后一行的 x 标签
```

---

## 间距优化技巧

### 减少分类图中的簇间距
```python
# 收紧分组间距
ax.set_xlim(-0.3, n_groups - 0.7)  # 而不是默认的 -0.5, n_groups - 0.5
```

### 最小化多行网格中的行间距
```python
fig.set_constrained_layout_pads(hspace=0.005)  # 非常小的值用于紧密行
```

### 复杂布局的 GridSpec 示例
```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(3, 4), dpi=300)

# 示例：顶部图例区域 + 主图 + 块注释
gs_top = fig.add_gridspec(1, 1, height_ratios=[0.12], top=0.95, bottom=0.88)
gs_main = fig.add_gridspec(1, 2, width_ratios=[0.25, 1.0], wspace=0.03,
                            left=0.05, right=0.95, top=0.85, bottom=0.1)

ax_legend = fig.add_subplot(gs_top[0, 0])
ax_block = fig.add_subplot(gs_main[0, 0])
ax_main = fig.add_subplot(gs_main[0, 1])
```

---

## 调试技巧

### 显示所有 axes 的边界
```python
# 用于调试布局问题
for ax in fig.axes:
    ax.set_facecolor('#f0f0f0')  # 浅灰色背景
    for spine in ax.spines.values():
        spine.set_edgecolor('red')
        spine.set_linewidth(2)
```

### 打印 axes 位置信息
```python
for i, ax in enumerate(fig.axes):
    pos = ax.get_position()
    print(f"Axes {i}: x0={pos.x0:.3f}, y0={pos.y0:.3f}, "
          f"width={pos.width:.3f}, height={pos.height:.3f}")
```

### 检查元素是否超出边界
```python
# 保存前检查
fig.canvas.draw()
for ax in fig.axes:
    bbox = ax.get_tightbbox(fig.canvas.get_renderer())
    print(f"Tight bbox: {bbox}")
```

---

## 快速修复检查清单

遇到布局问题时，按顺序尝试：

1. [ ] 使用 `bbox_inches="tight"` 保存
2. [ ] 检查字体配置是否在创建图表前设置
3. [ ] 尝试 `constrained_layout=True`
4. [ ] 适度增加图表尺寸（10-20%）
5. [ ] 检查旋转标签的对齐方式（`ha="center"`）
6. [ ] 调整 `wspace`/`hspace` 值（0.02-0.05）
7. [ ] 使用 GridSpec 进行精确控制
8. [ ] 验证所有文本元素 ≥6 pt
9. [ ] 检查 colorbar 位置和宽度
10. [ ] 在目标尺寸下预览图表
