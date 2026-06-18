# Journal-Specific Requirements

详细的顶级期刊投稿要求和标准。

## Nature/Cell/Science 通用标准

### 字体要求
- **字体系列**: Arial 或 Helvetica（无衬线字体）
- **最小可读尺寸**: 最终尺寸下 6 pt
- **推荐字号**:
  - 标题: 8-9 pt
  - 坐标轴标签: 7-8 pt
  - 刻度标签: 6-7 pt
  - 注释/图例: 6-7 pt

### 图表尺寸
- **单栏宽度**:
  - Nature: ~89 mm (3.5 inches)
  - Cell: ~85 mm (3.35 inches)
  - Science: ~90 mm (3.54 inches)
- **全宽**: ~180 mm (7 inches)
- **高度**: 通常不超过 225 mm (8.86 inches)

### 视觉要求
- **移除**: 顶部和右侧边框（使用 `sns.despine()` 或手动设置）
- **灰度测试**: 图表应在无色彩情况下可解读
- **线宽**: 0.5-1.5 pt（取决于图表类型）
- **标记大小**: 适中，避免过大或过小

### 分辨率要求
- **位图格式 (PNG/TIFF)**: 最低 300 DPI，推荐 600 DPI
- **矢量格式 (PDF/SVG)**: 优先使用，确保字体正确嵌入
- **组合图**: 如果包含位图元素，确保位图部分达到要求分辨率

## Nature 特定要求

### 配色方案
Nature 推荐的配色（来自 Nature Methods 指南）:
- 主色: `#0173B2` (蓝色)
- 辅助色: `#DE8F05` (橙色)
- 强调色: `#029E73` (绿色)

### 图表样式
```python
import matplotlib.pyplot as plt

# Nature 风格配置
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 7
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8
plt.rcParams['xtick.major.size'] = 2.5
plt.rcParams['ytick.major.size'] = 2.5

# 创建图表
fig, ax = plt.subplots(figsize=(3.5, 3))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
```

### 图例要求
- 位置: 通常在图表内部或紧邻图表
- 边框: 无边框或细边框
- 背景: 透明或白色

## Cell 特定要求

### 图表标注
- **面板标签**: 使用粗体大写字母 (A, B, C...)
- **标签位置**: 左上角，字号 9-10 pt
- **标签样式**: 黑色，无背景

### 统计标注
- **显著性标记**: 使用星号 (*, **, ***) 或 ns
- **P 值**: 如果显示具体值，使用科学计数法（P < 0.001）
- **误差线**: 明确标注是 SEM、SD 还是 CI

## Science 特定要求

### 颜色使用
- 避免使用纯红色和纯绿色的组合（色盲友好）
- 优先使用蓝色-橙色或蓝色-黄色组合
- 确保在灰度打印时仍可区分

### 多面板图
- 使用统一的字体大小和样式
- 保持一致的坐标轴刻度和标签格式
- 面板间距适中，避免过于拥挤

## 通用最佳实践

### 坐标轴
- **标签**: 始终包含单位（如 "Time (h)", "Expression (AU)"）
- **刻度**: 合理间隔，避免过密或过疏
- **范围**: 适当留白，不要让数据点紧贴边界

### 图例和标注
- **简洁**: 使用缩写时在图注中解释
- **位置**: 不遮挡数据点
- **一致性**: 同一图表系列中保持一致的符号和颜色

### 文件格式
- **提交**: 通常要求 TIFF、PDF 或 EPS
- **审稿**: PNG 或 PDF（便于在线查看）
- **最终版**: 高分辨率 TIFF 或矢量格式

## 投稿前检查清单

- [ ] 字体为 Arial/Helvetica，所有文本 ≥6 pt
- [ ] 图表尺寸符合期刊要求（单栏或全宽）
- [ ] 分辨率达到 600 DPI（位图）或使用矢量格式
- [ ] 配色方案色盲友好
- [ ] 通过灰度测试
- [ ] 移除不必要的边框和网格线
- [ ] 坐标轴标签包含单位
- [ ] 图例清晰且不遮挡数据
- [ ] 统计显著性标注清楚
- [ ] 多面板图标注一致
- [ ] 文件格式符合投稿要求
