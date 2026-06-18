# 后端选择（Python / R）

本 skill 支持 Python 与 R。**默认 Python**；仅在特定信号下必须询问或切换 R。选定后全程互斥，禁止 cross-backend preview/export。

## 默认策略

| 情况 | 行为 |
|---|---|
| 用户未指定，一般生信单图（UMAP、火山图、barplot 等） | **默认 Python**，直接执行 |
| 用户明确说 R / 提供 `.R`、RDS、Seurat 对象 | 用 **R** |
| 用户明确说 Python / 提供 `.py`、notebook、scanpy 流程 | 用 **Python** |
| 用户提到 **投稿/出版/manuscript/600 DPI** 且未指定后端 | **必须问「Python 还是 R？」** 后停止等待 |
| 用户提到 **ComplexHeatmap、ggtree、circlize、survminer、DESeq2 R 工作流** 且未指定后端 | **必须问「Python 还是 R？」** 或按上下文推荐 R 并确认 |
| 用户明确要求推荐后端 | 用决策表给出理由，确认后执行 |

**不要**在每次普通出图任务都阻塞询问；**不要**因「生信 = R」而默认 R。

## 互斥规则

选定后端后，以下**全部**须用同一后端完成：绘图脚本、预览、SVG/PNG/PDF 导出、视觉 QA。

**禁止** substitute preview 或 fallback export：

- 选了 R 但 `Rscript` 不可用 → 报告 blocker，给 R-only 脚本，**不用 Python 近似**。
- 选了 Python 但缺 `matplotlib` → 报告 blocker，给 Python-only 脚本，**不用 R 近似**。

非选定语言仅可用于非视觉数据准备（读 CSV、格式转换），不得 import 绘图库或保存图像。

## 生信场景决策表

| 倾向 R | 倾向 Python（默认） |
|---|---|
| ComplexHeatmap 多层注释热图 | scanpy / matplotlib 常规单图 |
| ggtree、circlize、survminer | UMAP、spatial、自定义 layout |
| 用户已有 ggplot2/ggprism 模板 | 自包含 Python 脚本 |
| Seurat R 对象为主 | AnnData / Python pipeline 为主 |

## 默认技术栈

### Python

| 库 | 角色 |
|---|---|
| seaborn + matplotlib | 主绘图 |
| adjustText | 标签防重叠 |
| matplotlib subplot_mosaic / GridSpec | 简单 2–4 panel 拼接 |

### R

| 库 | 角色 |
|---|---|
| ggplot2 + ggprism | 主绘图与学术主题 |
| ComplexHeatmap | 复杂注释热图 |
| ggrepel | 标签防重叠 |
| patchwork | 2–4 panel 简单拼接 |

> 含 hero panel、figure contract 的完整投稿页 → `nature-figure`。

## 缺失运行时

```bash
python -c "import matplotlib, seaborn; print('ok')"
Rscript -e "library(ggplot2); cat('ok\n')"
```

缺失则停止渲染，提供安装命令，**不切换后端**。
