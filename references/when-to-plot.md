# 何时创建图表

本 skill 覆盖：

- **单张生信数据图**（火山图、热图、UMAP、violin、dotplot 等）
- **简单多 panel 组合**（2–4 张同类型或互补数据图，用 patchwork / subplot 拼接，无 hero panel 论证链）

完整投稿 figure（hero panel、figure contract、schematic-led 复合论证）→ `nature-figure` skill。

## 默认原则（中等严格）

- **默认不主动生成图文件**。优先交付表格、统计结论、文字解读。
- 若一张图**能显著帮助理解**结果，可以**简短建议**出图（说明图类型与理由），等用户确认后再画；不要未经确认就直接 `savefig`。
- 用户**明确要求**画图 → 立即执行。
- 纯表格即可表达、且用户未要求可视化 → 不出图。
- 图表应 **minimal and purposeful**：每张 panel 只传达一个核心信息。

## 路由规则

| 需求类型 | 处理方式 | 说明 |
|---|---|---|
| 单张生信数据图 | 本 skill | seaborn/matplotlib 或 ggplot2 |
| 简单 2–4 panel 数据图组合 | 本 skill | patchwork（R）或 subplot_mosaic（Python） |
| 流程图、示意图、信息图 | **GenerateImage** | 大段文字、箭头逻辑、概念框架 |
| 复杂投稿 figure（hero panel、figure contract、schematic-led） | **nature-figure** | 论证链与整页编排 |
| 非生信通用图表 | 跳过本 skill | |
| 纯数据分析无画图需求 | 跳过 | 输出表格/数值；可建议但不自动生成图 |

## 简单 multi-panel vs nature-figure

| 特征 | 本 skill（简单组合） | nature-figure |
|---|---|---|
| Panel 数 | 通常 2–4 | 任意，常 4+ |
| 论证结构 | 各 panel 独立、并列展示 | hero panel + 证据层级 |
| 示意图 | 不含 workflow schematic（或另走 GenerateImage） | schematic-led composite |
| 工具 | patchwork / GridSpec | figure contract + 整页 QA |

## GenerateImage 触发条件

当用户需要以下类型时，**不要**用 matplotlib/ggplot2 硬画，改用 GenerateImage：

- 实验流程图、算法 pipeline 示意图
- 机制示意图、细胞通路概念图
- 含大量标注文字的信息图、poster 风格插图

若用户同时需要「数据图 + 示意图」，数据部分走本 skill，示意图走 GenerateImage。

## 与用户 memory 的优先级

1. 用户明确说「不要图」→ 不出图。
2. 用户 memory 中有偏好的图片格式 → 见 [export-policy.md](export-policy.md)。
3. 用户未指定且属于投稿/出版场景 → publication 导出档。
4. 用户未指定且属于日常沟通 → communication 导出档（SVG + PNG）。
