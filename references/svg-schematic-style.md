# SVG 模型架构图与数据流程示意图风格指南（AlphaEnzyme 范式）

整理自 *AlphaEnzyme*（Liu et al., bioRxiv 2026.11.04.764416v2）的 **Fig 1c（双模态模型架构图）** 与 **Fig 2b（数据清洗与队列构成概览图）**。本指南专为使用原生 SVG 或 `figgenie-paper-diagram` 绘制高颜值科研示意图提供可直接落地的视觉规范。

---

## 一、核心审美原则（为什么比普通黑框流程图高级）

1. **去死黑、去粗框**：正文与标注用柔和深炭灰 `#303030` 替代死黑 `#000000`；大容器外框尽量不用黑线，改用极淡的冰蓝/暖杏圆角底块完成空间分组。
2. **80 / 15 / 5 色彩克制法则**：
   - **80% 冷调钢青蓝单色阶**（主模态、模型主干、高亮结论）
   - **15% 暖杏沙色系**（第二模态、辅助输入、对照高亮）
   - **5% 焦糖朱橙 `#D55E04`**（全场仅点缀关键焦点、核心增益或活性位点）
3. **数据感微缩元件（Micro-visuals）替代纯文字框**：抽象张量/向量不写死文字 `"Embedding"`，而是画成 5–8 格水平/垂直分段渐变热图条；生物/化学输入直接嵌简笔线框图或轻透分子/细胞轮廓。

---

## 二、风格 A：双模态模型架构图（参考 AlphaEnzyme Fig 1c）

**适用场景**：Figure 1 模型总览图、多模态特征融合（如空间坐标 + 基因表达、RNA 序列 + 亚细胞图像）、Encoder–Head 推理框架。

### 1. 视觉布局骨架（左 $\rightarrow$ 中 $\rightarrow$ 右三段式）
- **左列（多模态输入卡，上下叠放）**：
  - **模态 1（如序列 / 基因表达 / 空间图）**：冰蓝浅底卡片 `fill="#F0F5FB"`, `stroke="#C4DDEC"`, `stroke-width="0.6"`, `rx="4"`；卡内放文字标题 + 微缩实体示意（如残基串珠、细胞点云）。
  - **模态 2（如化学结构 / 图像 / 先验图谱）**：暖杏浅底卡片 `fill="#FCF0E9"`, `stroke="#F9D9C5"`, `stroke-width="0.6"`, `rx="4"`；卡内放对应微缩示意。
- **中间桥接卡（可选，强调统一框架/基础模型身份）**：
  - 纵向圆角卡片，使用**上冰蓝 `#DBE9F6` $\rightarrow$ 下暖杏 `#F9E0D1` 垂直线性渐变**，视觉上把上下两路输入柔和融合，居中放简洁几何徽标与模型名。
- **右列（核心主干大容器）**：
  - 外层大容器采用无压迫感的冰蓝底 `fill="#F0F5FB"`, `stroke="#C4DDEC"`, `stroke-width="0.6"`, `rx="6"`。
  - **上分支（主干计算流）**：浅冰蓝子模块 `fill="#DBE9F6"`, `stroke="#93C3DD"`, `stroke-width="0.6"`, `rx="3"`（如 `Input → Encoder → Graph/Attention → Fusion`）；若有迭代循环（如 `Recycling`），在顶部拉一条干净的**直角圆角回环箭头**（`stroke="#303030"`, `stroke-width="0.7"`），文字打断线段居中。
  - **下分支（多模态特征拼接示意）**：
    - 模态 1 编码器（白底蓝边卡）$\rightarrow$ 输出画成 **水平 1D 蓝色渐变分格条**（6–8 个紧贴小方格，色阶 `#DCEAF5 → #93C3DD → #316F98 → #195E8D`）；
    - 模态 2 编码器（浅杏底 `#FCF0E9`、暖杏边 `#F9D9C5`）$\rightarrow$ 输出画成 **水平 1D 暖杏渐变分格条**（色阶 `#FCF0E9 → #F9D9C5 → #EABB8E → #D55E04`）；
    - 两路汇入一个小圆圈算子 `⊕`（融合/拼接），转为一根**垂直拼接张量条（上半蓝阶 + 下半杏阶）**，送入浅冰蓝竖长模块 `Output Head`，右侧水平扇出 2–4 个下游任务名称（纯文字无多余方框，保持呼吸感）。

### 2. Fig 1c 精确 SVG Token 速查表

| 视觉元素 | `fill` | `stroke` | `stroke-width` | `rx` |
|---|---|---|---|---|
| 大架构外容器 / 模态 1 输入卡 | `#F0F5FB` | `#C4DDEC` | `0.6 pt` | `4–6 pt` |
| 模态 1 内部子模块 | `#DBE9F6` | `#93C3DD` | `0.6 pt` | `3 pt` |
| 模态 2 输入卡 / 编码子块 | `#FCF0E9` | `#F9D9C5` | `0.6 pt` | `4 pt` |
| 模态 1 微缩特征条色阶 | `#DCEAF5 → #93C3DD → #498CAE → #195E8D` | `#FFFFFF` (`0.3 pt`) | — | `0` |
| 模态 2 微缩特征条色阶 | `#FCF0E9 → #F9D9C5 → #EABB8E → #D55E04` | `#FFFFFF` (`0.3 pt`) | — | `0` |
| 连线、箭头与正文炭灰 | `#303030` | `#303030` | `0.65–0.8 pt` | — |

---

## 三、风格 B：数据清洗流程 + 单点聚焦队列统计图（参考 AlphaEnzyme Fig 2b）

**适用场景**：数据集构建与质控筛选流程（如 STRAND 35 套空间转录组数据筛选）、训练/测试时间切分说明、多来源样本队列构成概览。

### 1. 视觉布局骨架（上流程 + 下双缩略数据图）
- **上半区（极简黑白线框筛选管线）**：
  - **绝不花哨填色**：所有清洗步骤统一用**纯白圆角框** `fill="#FFFFFF"`, `stroke="#303030"`, `stroke-width="0.8"`, `rx="3"`；
  - 起始节点内嵌极简黑色线稿图标（如数据库圆柱图标），末尾节点展示**数据集切分逻辑**（如一条竖直时间轴 `old ↑ new` 配合水平虚线截止日期 `2023.07`，上下分叉指向 `Test set` 与 `Training set` 两个白底圆角框）。
- **下半区（紧贴管线下方，左右并排 2 张微缩队列统计图 — 「全灰单点蓝」聚焦法）**：
  - **左缩略图（类别构成饼图 / 环形图）**：其余类别全部采用冷灰阶（`#E3E6EB`、`#CFD0D1`、`#ADB4BC`、`#9199A3`、`#7D8591`，白色 `0.6 pt` 分割缝），**只将最主要或最核心的一个类别扇区高亮为钴钢蓝 `#2066AC`**；标签环绕外侧直标名称与百分比（不放额外图例）。
  - **右缩略图（规模/长度分布直方图）**：所有柱体采用浅冷灰 `fill="#CFD0D1"`, `stroke="#303030"`, `stroke-width="0.5"`，**只将峰值/主分布柱高亮为钴钢蓝 `#2066AC`**；柱顶直接标百分比，右上空白处附一句 `median: xxx`；去上右边框（`despine`）。

### 2. Fig 2b 精确 SVG Token 速查表

| 视觉元素 | `fill` | `stroke` | `stroke-width` | 说明 |
|---|---|---|---|---|
| 清洗步骤方框 | `#FFFFFF` | `#303030` | `0.8 pt` | 纯白无阴影，保持高对比清爽感 |
| 流程箭头与时间虚线 | `#303030` | `#303030` | `0.75 pt` | 切分阈值线用 `stroke-dasharray="2.5 2"` |
| 背景常规扇区 / 柱体 | `#CFD0D1`（多类扩至 `#E3E6EB`–`#7D8591`） | `#FFFFFF`（饼图）/ `#303030`（柱图） | `0.5–0.6 pt` | 全灰降噪 |
| **唯一主角扇区 / 峰值柱** | **`#2066AC`** | `#FFFFFF` / `#303030` | `0.5–0.6 pt` | 视觉唯一焦点，直指核心结论 |

---

## 四、SVG 图标库一键检索与安全内联（`scripts/fetch_icon.py`）

画模型架构图、数据清洗流程图或机制示意图时，**不要从零手搓粗糙的几何图标**，直接使用本仓库自带的 `scripts/fetch_icon.py`（免鉴权、自动缓存至 `~/.cache/bio-plot-icons/`、自动给 `id` 与 `.cls-*` CSS 类加唯一前缀防样式串扰、自动等比缩放入目标方框）。

### 1. 支持的两大图标源（通用工程 + 生命科学全覆盖）

| 类型 | 入口前缀 / 来源 | 覆盖库与规模 | 适用元素 | 许可提醒 |
|---|---|---|---|---|
| **通用工程 / 流程** | **Iconify**（`lucide:`、`ph:`、`heroicons:`、`tabler:`） | 30 万+ 矢量图标（聚合 Lucide 1800+、Phosphor 9000+、Heroicons 1200+、Tabler 6200+） | 数据库、过滤漏斗、芯片/GPU、代码、文件夹、锁、显微镜简笔 | ISC / MIT（免费商用与论文发表，无需署名） |
| **生命科学 / 医学** | **Bioicons**（`bioicons:`） | 2,829 个纯矢量 SVG（**已内置 1,375 个 Servier Medical Art + 634 个 DBCLS 图标**） | 细胞、亚细胞器、RNA/DNA、96 孔板、显微镜、测序仪、小鼠、器官、化学分子 | `CC-0` 免费免署名；`CC-BY`（含 Servier / DBCLS）须在图注或致谢注明出处 |

> **风格统一规则**：同一张图内的**逻辑/工程图标**统一只用 **`lucide:`**（细线圆角，与 `0.6–0.8 pt` 线宽和 AlphaEnzyme 风格最搭，不要混用粗实心与细线）；**生物实体图标**用 **`bioicons:`**，必要时传 `--color "#316F98"` 单色化融入整图主色调。

### 2. CLI 一行命令用法

```bash
SCRIPT=~/.claude/skills/bioinformatics-plotting-standards/scripts/fetch_icon.py

# 1) 同时检索通用图标 + 生物图标（支持 --source all|iconify|bioicons）
python3 "$SCRIPT" search "database" --limit 6
python3 "$SCRIPT" search "rna" --source bioicons --limit 8
python3 "$SCRIPT" search "microscope" --limit 6

# 2) 下载、清洗命名空间并改色为独立 SVG
python3 "$SCRIPT" fetch lucide:database --color "#316F98" --stroke-width 1.6 -o icon_db.svg
python3 "$SCRIPT" fetch bioicons:dna-2 --color "#316F98" -o icon_dna.svg
python3 "$SCRIPT" fetch bioicons:96_well_plate_cells -o icon_plate.svg   # 不传 --color 保留原色

# 3) 直接输出可嵌进主图的内联 <g> 片段（自动缩放居中至 (x, y) 的 size×size pt 盒内）
python3 "$SCRIPT" fetch lucide:filter --inline-g --x 12 --y 24 --size 14 --color "#303030"
```

### 3. 在 Python SVG 生成脚本中直接调用

```python
import sys
sys.path.insert(0, "/home/wzx/.claude/skills/bioinformatics-plotting-standards")
from scripts.fetch_icon import inline_icon_g

# 直接返回已清洗命名空间、无外链依赖的 <g> 字符串（完全通过 FigGenie lint.py 检查）
g_db    = inline_icon_g("lucide:database", x=10, y=10, size=18, color="#316F98", stroke_width=1.6)
g_plate = inline_icon_g("bioicons:96_well_plate_cells", x=80, y=8, size=24)  # 保留原色
g_dna   = inline_icon_g("bioicons:dna-2", x=120, y=8, size=24, color="#316F98")
```

> **禁止外链**：绝不用 `<image href="https://...">` 引入网络图标；一律使用 `inline_icon_g()` 内联矢量路径，保证离线打开、矢量 PDF 导出与 `FigGenie` Linter 100% 通过。

---

## 五、与 `figgenie-paper-diagram` 联动提示

使用 `figgenie-paper-diagram` 绘制论文框架图或数据流程图时，可直接声明：
- **「按 `svg-schematic-style.md` 的 AlphaEnzyme Fig 1c 风格绘制」** $\rightarrow$ 启用双模态冰蓝/暖杏无黑框底色卡 + 1D 渐变张量条 + `#303030` 炭灰文字；
- **「按 `svg-schematic-style.md` 的 AlphaEnzyme Fig 2b 风格绘制」** $\rightarrow$ 启用纯白细黑框清洗流程 + 下方全灰单点钴蓝 `#2066AC` 队列统计缩略图；
- 需要丰富图标时，直接调用 `scripts/fetch_icon.py` 检索并内联 **Lucide / Phosphor / Heroicons / Tabler** 与 **Bioicons（含 Servier）** 矢量图标。
- 字体与尺寸仍遵循本仓库默认规范（毕业论文模式：`Arial`、`text-rendering="geometricPrecision"`、宽 $\le 446\text{ pt}$、正文 `7.5 pt`、大写 `10 pt` 面板字母）。
