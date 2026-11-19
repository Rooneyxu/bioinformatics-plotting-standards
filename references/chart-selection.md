# 生信与计算方法学高表现力图型选型指南（Chart Selection）

参考 [From Data to Viz](https://www.data-to-viz.com/) 的数据形态决策树与 *Nature Methods* / *Nature Machine Intelligence* / *Nature Communications* 图表范式整理。

## 选型总则

1. **尊重明确指令**：用户已点名具体图型（如「画 barplot」「画火山图」「画热图」）时，按用户指定图型绘制；仅在存在严重可读性缺陷（如 $\ge 4$ 集合画 Venn、数万散点严重过绘）时简短提醒更优替代。
2. **开放需求主动升维**：当用户只描述数据或科学结论（「展示这几个方法在各数据集的表现」「看看这些特征的相关性」「对比处理前后的得分」「可视化亚细胞径向分布」）而未锁死图型时，**按下方数据结构匹配高信息密度图型**，替代信息量偏低的纯箱线图、带误差棒粗柱状图或单一色块热图。
3. **成熟库优先、缺包先问**：优先调用 Python / R 标准栈或本机已安装的成熟包；若某个专用包（如 R `funkyheatmap`、`ggalluvial`、`ggdist`，Python `upsetplot`、`shap`）能大幅减少代码量并提升出版质量但本机未安装，先向用户说明包名与优势，确认后再安装，不硬写脆弱的手工几何拼接。

---

## 一、分布对比与梯度推移（替代纯 Boxplot / 误差棒柱状图）

> **Data-to-Viz 核心避坑**：纯箱线图会隐藏双峰分布（Bimodality）与各组真实样本量差异；均值+误差棒柱状图（Dynamite plot）对偏态分布极具误导性。

### 1. 云雨图（Raincloud Plot）与小提琴+箱线叠画
- **适用场景**：比较 2–8 个细胞亚群、实验条件或算法预测得分的连续分布，尤其当分布可能存在双峰、长尾或组间样本量悬殊时。
- **视觉编码**：
  - **云雨图**：单侧半小提琴（核密度形态）+ 窄箱线（中位数与四分位）+ 另一侧抖动原始点（样本量 $n \le 200$/组时叠加散点，$n$ 过大时省去散点或改用分位点）。
  - **紧凑叠画**：多组并排空间受限时，直接使用本 Skill 内置的 `scripts/violin_boxplot.py`（Li Lab 风格小提琴+箱线同轴叠画，见 [violin-boxplot.md](violin-boxplot.md)）。
- **实现路径**：
  - **R**：`ggdist::stat_halfeye()` + `geom_boxplot(width = 0.12)` + `ggdist::stat_dots()`（或 `ggrain::geom_rain()`）。
  - **Python**：紧凑叠画优先用 `scripts/violin_boxplot.py`；标准云雨图可用 `matplotlib` 裁剪 `violinplot` 半侧顶点（clip path / vertices）配合窄 `boxplot` 与 `sns.stripplot`，或已安装时的 `ptitprince.RainCloud`。

### 2. 配对哑铃图 / 斜率图（Dumbbell Plot / Paired Slopegraph）
- **适用场景**：同一批数据集、细胞系、患者样本或基因簇在**两种状态/方法前后**的成对比较（如 `Pure GEX → Spatial-fused`、`Raw → Majority Voting`、消融核心模块前后）。
- **视觉编码**：每个实体占一行（哑铃图，适合 5–25 个数据集/亚群）或左右两列连线（斜率图，适合 3–10 个组别）；两端圆点用对比色区分前后状态，中间细线段连接（可按提升方向正负着色），**纵轴按目标方法得分或提升幅度排序**。
- **实现路径**：
  - **Python**：`ax.hlines(y, xmin, xmax, color='#BEBEBE', lw=1.2)` + 两组 `ax.scatter()`，原生 `matplotlib` 10 行即可稳定实现。
  - **R**：`geom_segment(aes(x = before, xend = after, y = item, yend = item))` + `geom_point()`（或 `ggalt::geom_dumbbell`）。

### 3. 山脊图（Ridgeline / Joyplot）
- **适用场景**：展示连续变量沿**有序梯度**（4–12 层）的分布迁移，如：
  - 亚细胞空间转录组中沿「核中心 $\rightarrow$ 核膜 $\rightarrow$ 胞质 $\rightarrow$ 质膜」归一化径向距离的 RNA 密度推移；
  - 单细胞发育伪时间（Pseudotime）分箱或空间组织层（Cortical layers / 肝小叶门管区-中央静脉轴）表达分布；
  - 不同噪声水平 / Dropout 比例梯度下算法指标的退化曲线。
- **避坑规则**：组数控制在 4–12 层（$<4$ 层直接用分组核密度曲线，`>12` 层改用按峰值排序的热图）；层间重叠度（overlap）适中，确保后方波峰不被完全遮挡。
- **实现路径**：
  - **R**：`ggridges::geom_density_ridges(scale = 1.4, alpha = 0.75)`。
  - **Python**：`seaborn.FacetGrid(row=..., aspect=4, height=0.6)` 叠加 `sns.kdeplot(fill=True)` 并设 `hspace=-0.35` + 透明背景，或已安装的 `joypy`。

---

## 二、排序与效应量展示（替代粗重柱状图）

### 4. 排序棒棒糖图 / 克利夫兰点图（Ordered Lollipop / Cleveland Dot Plot）
- **适用场景**：单维数值排名展示，如消融实验各模块 $\Delta$ 增益、特征重要性 Top 20、GO/KEGG 通路富集 $-\log_{10}(\text{FDR})$ 或 NES 双向得分。
- **视觉编码**：细线段（从 0 或基准线出发）+ 末端圆点（圆点大小可编码基因数/样本数，颜色可编码显著性或正负方向）。**必须先按数值大小排序（Order your data）**，水平放置（`barh` / `y` 轴放名称）避免长标签旋转。
- **实现路径**：
  - **Python**：`ax.hlines(y, baseline, values, lw=1.0)` + `ax.scatter(values, y, s=sizes, c=colors, zorder=3)`。
  - **R**：`ggplot(df, aes(x = reorder(name, val), y = val)) + geom_segment(aes(xend = name, y = 0, yend = val)) + geom_point() + coord_flip()`。

---

## 三、多变量相关与大样本双变量关系（替代基础散点 / 普通相关热图）

### 5. 异构混合相关矩阵（Asymmetric Correlogram）
- **适用场景**：3–8 个连续变量的成对关系全景检查，如跨空间转录组平台（MERFISH / seqFISH / Xenium / CosMx）丰度一致性、生物学重复（Rep1–Rep3）可重复性、手工理化特征与深度学习 Embedding 主成分的正交性验证。
- **视觉编码**（比纯 `sns.pairplot` 散点或纯色块热图信息密度高得多）：
  - **下三角**：2D 核密度等高线（`kdeplot`）或 `hexbin` + 线性/稳健回归线（解决数千基因/细胞的散点过绘黑团）；
  - **对角线**：单变量核密度曲线或直方图（有分组时按分类叠画）；
  - **上三角**：气泡大小 + 发散配色（默认 Nature 紫–绿）编码 Pearson / Spearman $r$ 值与显著性星号。
- **避坑规则**：**变量数严格 $\le 8$**；超过 8–10 个变量时字号与子图过小无法阅读，应改用聚类相关热图（Clustered Heatmap）或筛选核心代表变量。
- **实现路径**：
  - **Python**：`seaborn.PairGrid(df, corner=False)`，分别调用 `g.map_lower(sns.kdeplot)`、`g.map_diag(sns.kdeplot)` 与自定义 `g.map_upper(corr_bubble_func)`。
  - **R**：`GGally::ggpairs()` 自定义 `upper` / `lower` / `diag` 函数，或 `corrplot` 混合模式（`corrplot.mixed`）。

### 6. 边际分布散点 / 等高线图（Marginal KDE / Hexbin Scatter）
- **适用场景**：重点剖析两个核心连续变量的耦合关系及各自边缘分布（如 RNA 表达丰度 vs 亚细胞空间聚集度 Ripley's L、序列相分离倾向评分 vs 颗粒富集倍数）。
- **视觉编码**：主面板用半透明散点 + 2D 等高线（样本量 $>3000$ 时改用 `hexbin` 或栅格化密度 + 外围离群点），上侧与右侧紧贴 1D 核密度或箱线边缘轴，关键代表性基因用斜体 + `adjustText` / `ggrepel` 引线标注。
- **实现路径**：
  - **Python**：`seaborn.JointGrid`（`plot_joint` + `plot_marginals`）或 `GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4])`。
  - **R**：`ggExtra::ggMarginal(p, type = "density", groupColour = TRUE, groupFill = TRUE)` 或 `patchwork` 拼接主图与边缘密度。

---

## 四、方法学综合 Benchmark、集合交集与效率权衡

### 7. Funkyheatmap（多几何图形综合评测表）
- **适用场景**：计算生信方法学论文（如 *Nature Methods* `scIB` 风格）汇总 **多个方法 × 多类数据集 × 多种指标类型（准确性、生物保守性、跨平台泛化、运行耗时、显存占用）** 的终极总览表。
- **视觉编码**：按综合总分降序排列各方法行；不同指标分组采用语义化几何编码——**总分**用横向进度条（bar），**子任务得分**用圆角矩形或圆点（大小+颜色双编码），**排名或资源消耗**用微缩柱图或文本徽章，顶部用分组色块区分指标大类。
- **实现路径**：
  - **R（首选官方实现）**：`funkyheatmap::funky_heatmap()`（社区标准库，出图极稳）。
  - **Python**：使用 `matplotlib` 分列 `GridSpec` 或单轴网格坐标组合 `barh` + `scatter`（控制圆点面积正比于归一化分值），列数不宜过多（建议 $\le 12$ 列）以保证紧凑可读。

### 8. 分轴归一化雷达图（Normalized Radar / Polar Chart）
- **适用场景**：在 5–8 个正交评测维度（如聚类 ARI、亚细胞定位精度、抗噪稳定性、跨平台迁移、批次消除、速度）上对比本方法与 2–3 个代表性 Baseline 的整体均衡性。
- **避坑规则**：方法曲线数 **$\le 4$ 条**，填充透明度极低（`alpha=0.05–0.10`）防止遮挡；若各轴量纲不同，必须按轴独立归一化并在轴旁注明量程；多于 4 个方法或维度无闭合对比意义时，改用平行坐标图（Parallel Coordinates）或分组点图。
- **实现路径**：
  - **Python**：`fig.add_subplot(111, projection='polar')`，`ax.set_theta_zero_location('N')`，去除默认圆形网格改画多边形等值线。
  - **R**：`ggradar::ggradar()` 或 `fmsb::radarchart()`。

### 9. 精度—效率帕累托前沿气泡图（Pareto Frontier Bubble Plot）
- **适用场景**：证明新算法兼具高精度与高可扩展性（Scalability）。
- **视觉编码**：横轴为运行时间或峰值显存（跨数量级时取 $\log_{10}$ 尺度），纵轴为核心精度指标（ARI / Macro-F1 / AUROC），气泡大小编码测试细胞数或转录本规模，用阶梯虚线标出**帕累托最优前沿（Pareto Frontier）**，直接高亮本方法位于最优角。
- **实现路径**：`matplotlib` `ax.scatter()` + `ax.set_xscale('log')` + `adjustText` 标注方法名（替代拥挤图例）。

### 10. UpSet 图（UpSet Plot，替代多组 Venn 图）
- **适用场景**：比较 **$\ge 4$ 个集合**的交集结构（如 4 种空间平台检出的亚细胞特异定位基因交集、5 种差异/聚类算法检出结果的共识度）。
- **视觉编码**：下方交集点阵连接指示集合组合，上方柱状图显示交集大小，右侧条形图显示各原始集合总量；上方还可叠加子面板（如各交集基因的平均表达量或相分离评分箱线图）。
- **避坑规则**：2–3 组简单交集可用比例面积 Venn 图；**一旦集合数 $\ge 4$，一律使用 UpSet Plot**，禁止画扭曲难读的四叶/五叶韦恩图。
- **实现路径**：
  - **R**：`ComplexUpset::upset()`（支持叠加 `ggplot2` 属性子面板）或 `UpSetR::upset()`。
  - **Python**：`upsetplot.UpSet()`；若未安装且仅需紧凑展示前 10 大交集，可用 `GridSpec(2, 1)` 上画排序柱图、下画点阵连线矩阵（约 25 行原生 `matplotlib`）。

---

## 五、跨层流向、聚类重分配与网络关系

### 11. 冲积图 / 桑基图（Alluvial / Sankey Diagram）
- **适用场景**：展示离散类别在 **2–4 个层级或阶段**之间的流转、分裂与合并，非常适合：
  - 不同空间/单细胞聚类方法之间的簇对应关系（如 `Pure GEX clusters → Banksy → GRASP`）；
  - 细胞类型自动注释在空间平滑或投票修正前后的标签重分配（`Raw prediction → Spatial refined`）；
  - 「RNA 亚细胞定位模式簇 $\rightarrow$ 所属细胞器 $\rightarrow$ 生物学通路/功能态」的多层映射。
- **避坑规则**：每层类别数控制在 $\le 10$（尾部极小簇合并为 `Other`），调整各层节点纵向顺序以**最小化流带交叉**；流带使用 `alpha=0.45–0.65` 半透明填充。
- **实现路径**：
  - **R（最优雅）**：`ggalluvial`（`geom_alluvium` + `geom_stratum`）或 `ggsankey`。
  - **Python**：`matplotlib.path.Path` 三次贝塞尔曲线（Cubic Bézier ribbon）绘制静态矢量冲积带（保证导出纯矢量 PDF/SVG，避免 `plotly` 位图化或交互样式违和）。

### 12. 弦图（Chord Diagram）
- **适用场景**：展示具有权重强度的节点间对称共现或有向通讯（节点数 4–12 个），如组织空间微环境中细胞类型邻域共定位富集（Neighborhood Enrichment）、不同亚细胞区室间的转录本共定位网络、CellChat 配受体细胞通讯总强度。
- **避坑规则**：连线过多会变成“毛线球”——仅保留统计显著或权重 Top 的边，弱背景边降透明度或置灰。
- **实现路径**：
  - **R**：`circlize::chordDiagram()`。
  - **Python**：`pycirclize`（`Circos.initialize_from_matrix`）或 `mne_connectivity.viz.plot_connectivity_circle`。

---

## 六、模型可解释性与特征归因

### 13. SHAP 蜂群图（SHAP Beeswarm / Summary Plot）
- **适用场景**：机器学习或序列+空间多模态融合模型（如手工理化特征、k-mer、空间邻域统计量）的全局可解释性分析，同时回答「哪些特征最重要」与「高特征值是正向推动还是负向抑制预测」。
- **视觉编码**：纵轴按平均 $|\text{SHAP value}|$ 降序排列 Top 10–15 特征，横轴为样本级 SHAP 值（围绕 `x=0` 竖线展开），点纵向按密度抖动成蜂群状，点颜色使用色盲友好渐变（如 `plasma` 或 Nature 紫–绿）编码特征自身数值高低。
- **实现路径**：
  - **Python**：`shap.plots.beeswarm(shap_values, show=False)` 后接本 Skill 字体、`despine` 与 600 DPI / PDF / SVG 导出规范。
  - **R**：`shapviz::sv_importance(shp, kind = "beeswarm")`。

---

## 七、方法学与评测高阶组合图型（AlphaEnzyme / Nature Methods 实战范式）

> 面向计算生物学 / AI 方法学论文（多数据集基准评测、OOD 泛化、筛选预算、候选排序与队列展示），可直接与 `scripts/alphaenzyme_colors.py` 搭配使用。

### 14. 热图 + 共享纵轴箱线图 + Top-$k$ 胜率条三联图（Heatmap + Marginal Boxplot + Win-Rate Strip）
- **原型参考**：*AlphaEnzyme* Fig 3f。
- **适用场景**：在多个独立数据集/折/蛋白任务（如 8–35 个空间转录组数据集或留一法交叉验证折）上综合比较 5–10 个方法，既想看清**逐数据集明细**，又想直接总结**跨数据集稳定性**和**进入前三/第一的胜率**。
- **视觉编码**：严格共享 Y 轴（按综合表现排序各方法行）——**左面板**画逐数据集指标热图（推荐 `get_alphaenzyme_blue_cmap()`）；**中面板**紧贴热图右侧画各方法跨数据集分布的横向窄箱线图（本方法高亮钢蓝、其余冷灰）；**右面板**紧贴一根横向微缩条展示 `Top-1 / Top-3 frequency` 并在条尾直接标百分比。
- **实现路径**：
  - **Python**：`GridSpec(1, 3, width_ratios=[4.5, 2.0, 1.3], wspace=0.08)` + `sharey=ax_heat`，中右两轴关闭 `yticklabels`。
  - **R**：`patchwork` 水平拼接 `geom_tile()` + `geom_boxplot()` + `geom_col()` 并设 `plot_layout(widths = c(4.5, 2, 1.3))`。

### 15. 均值柱/散点 + 配对差值 $\Delta$ 置信区间森林图（Paired $\Delta$ Bootstrap Forest Plot）
- **原型参考**：*AlphaEnzyme* Fig 2e–f（亦呼应 Gardner–Altman Estimation Plot）。
- **适用场景**：在相同查询集/样本集上对比本方法与多个 Baseline，替代仅在柱顶标 `* / ** / ***` 的传统做法，直观交代**绝对性能**与**相对每个 Baseline 的配对净增益及 95% Bootstrap 置信区间**。
- **视觉编码**：**左面板**画分组柱状图（Fig 2e 冷灰阶 + 主角钢蓝 `#2C6C9B`），叠加各折/子集空心白底圆点（`facecolor='white'`）与误差棒；**右面板**以各 Baseline 为纵轴，画 `x = 0` 竖虚线，正增益区铺极淡冰蓝底 `#F0F5FB`，用钢蓝点+横误差棒画配对差值 $\Delta$ 与 95% CI（右侧直标 `+0.13` 等数值，误差棒完全在 0 右侧即严格显著）。
- **实现路径**：`GridSpec(1, 2, width_ratios=[2.2, 1.2])`，右图用 `ax.errorbar(..., fmt='o', capsize=2)` + `ax.axvline(0, ls='--', color='#8C8C8C')` + `ax.axvspan(0, xmax, color='#F0F5FB', zorder=0)`。

### 16. 双阈值四象限 OOD 难度分层图（2D Stratification Quadrant Plot）
- **原型参考**：*AlphaEnzyme* Fig 2g。
- **适用场景**：剖析模型泛化边界，证明「在分布外（OOD）或高难度样本上本方法依然领先」（如横轴放序列相似度/空间密度，纵轴放特征相似度/转录本稀疏度）。
- **视觉编码**：散点按目标指标连续着色（钢青蓝单色阶），用**横竖两条虚线阈值**将平面切成 Q1–Q4 四个象限（标注各象限样本数或区域名称），在左下/右下空白处嵌一张 **Inset 微缩柱状图**汇总四个象限的均值对比（仅高亮最难 OOD 象限柱体为深蓝 `#2066AC`）。
- **实现路径**：主图 `ax.scatter()` + `ax.axvline()` / `ax.axhline()` + `ax.inset_axes([0.55, 0.08, 0.40, 0.32])` 画四象限汇总柱图。

### 17. 筛选预算—收益带状曲线（Budget / Top-$k$ Enrichment Ribbon）
- **原型参考**：*AlphaEnzyme* Fig 2c & Fig 4c。
- **适用场景**：横轴为递增的资源/候选预算（如筛选 Top-8 $\rightarrow$ Top-32 候选变体、空间 Gene Panel 基因数 $50 \rightarrow 500$、采样细胞数比例），纵轴为命中率、nDCG 或聚类保持度。
- **视觉编码**：本方法用深钢蓝实线 + 圆形 Marker + 半透明阴影带（`alpha=0.18`，表 SEM 或 95% CI）；各 Baseline 用冷灰/暖沙虚线配不同形状 Marker（`THESIS_MARKERS`），清晰呈现全预算区间内的持续领先。
- **实现路径**：`ax.plot()` + `ax.fill_between(x, mean - sem, mean + sem, alpha=0.18)`（Python）；`geom_ribbon()` + `geom_line()` + `geom_point()`（R）。

### 18. 排序瀑布柱图 + 留白内嵌属性表 + 画中画阴性对照窗（Waterfall + Embedded Table & Insets）
- **原型参考**：*AlphaEnzyme* Fig 5d。
- **适用场景**：展示 Top-20 至 Top-50 候选基因/突变体/细胞亚群的实验验证或打分排序（典型呈左高右低长尾陡降分布，右上方天然空出大片留白）。
- **视觉编码**：柱体按实测值降序排成瀑布（超越对照线的正向命中用钢蓝/暖杏高亮，其余浅灰，叠加生物学重复散点与均值误差棒，画一条水平对照基线 `y = 1.0`）；**直接利用右上大块留白**，左侧嵌一块极简微缩属性表（列出 Top 命中项的关键突变/特征），右侧嵌 1–2 个画中画小窗（`inset_axes` 展示阴性对照/随机筛选组结果或整体命中率饼图），一张图闭环讲完湿实验/筛选验证。
- **实现路径**：`ax.bar()` + `ax.table()`（或精准排版文本框）+ `ax.inset_axes()`。

### 19. 数据集队列构成与清洗概览组合板（Cohort Curation & Spotlight Strip）
- **原型参考**：*AlphaEnzyme* Fig 2b（SVG 风格细则见 [svg-schematic-style.md](svg-schematic-style.md)）。
- **适用场景**：展示自建/整合的大规模多平台数据集（如 35 套空间转录组数据）的来源筛选、训练/测试集划分与样本组成。
- **视觉编码**：顶部为纯白细黑框数据清洗管线 + 时间/平台切分叉；下方紧贴「全灰单点蓝 `#2066AC`」风格的微缩类别饼图与规模分布直方图（只把占比最大或最核心的类别/峰值柱标蓝，其余全灰降噪）。
- **实现路径**：纯数据组合可用 Python `GridSpec`（顶部 `axis('off')` 流程 + 下方 `pie` & `bar`）；追求极致矢量排版可走 SVG / `figgenie-paper-diagram`。

---

## 快速选型检查表（写代码前自检）

| 你的初始念头 | 先停一秒自问 | 更具表现力的升级方案 |
|---|---|---|
| 画普通 Boxplot | 分布是否有双峰/偏态？样本量是否值得展示？是否是同一批对象的成对前后对比？ | 多组分布 → **Raincloud / Li Lab Violin+Box / AlphaEnzyme Fig 2d**；成对前后 → **Dumbbell / Slopegraph**；沿连续梯度 → **Ridgeline** |
| 画普通 Barplot | 是否是单维排名？是否带多折/多样本对比各 Baseline？是否呈长尾 Top-$N$ 瀑布分布？ | 单维排名/消融 → **Ordered Lollipop**；多方法对比 → **均值柱 + 配对 $\Delta$ 森林图（#15）**；Top-$N$ 筛选验证 → **瀑布柱 + 内嵌表/画中画（#18）** |
| 画普通色块 Heatmap | 是否是 3–8 个连续变量看相关？是否是多方法跨多数据集的 Benchmark？ | 3–8 变量相关 → **Asymmetric Correlogram**；多方法跨数据集 → **热图+共享纵轴箱线+胜率条三联图（#14）** 或 **Funkyheatmap（#7）** |
| 画普通 Scatter | 点数是否 $>1000$ 导致糊成一团？是否在论证双维度难度分层（OOD 泛化）？ | 大样本双变量 → **2D KDE / Hexbin + Marginal Density**；难度分层泛化 → **双阈值四象限图 + Inset 汇总柱（#16）** |
| 画普通折线图 | 横轴是否是候选数/基因数预算，且有多折重复？ | 预算递增收益 → **预算—收益带状曲线（#17，带 SEM/CI 阴影与不同 Marker）** |
| 画多组 Venn 图 | 集合数是否 $\ge 4$？是否还想看各交集子集的定量特征？ | $\ge 4$ 组交集 → **UpSet Plot**（可叠属性箱线面板） |
| 画混淆矩阵看聚类对比 | 是否在讲“亚群分裂/合并/重分配”或跨层映射的故事？ | 2–4 层类别流转 → **Alluvial / Sankey Diagram** |
| 介绍自建/汇总数据集 | 是否要同时说清筛选流程、数据集切分和样本构成分布？ | 队列概览 → **数据集队列清洗与单点蓝高亮组合板（#19）** |
