# bioinformatics-plotting-standards

面向 **生物信息学单图与简单多 panel（2–4）** 的出版级绘图 Agent Skill，适用于 Cursor、Claude Code、Codex 等支持 `SKILL.md` 的 Agent 环境。

典型图表：火山图、热图、UMAP/t-SNE、violin、dotplot、Manhattan/GWAS、spatial、barplot 等。

---

## 来源与致谢

本 Skill **不是从零编写**，而是在以下两份规范基础上整合、裁剪并针对 Agent 工作流做了大量改写与验证：

| 来源 | 说明 |
|------|------|
| [**Yuan1z0825/nature-skills**](https://github.com/Yuan1z0825/nature-skills) | 符合 Nature 论文学术表达与科研绘图的 Skill 集合；本仓库主要借鉴其中的 **`nature-figure`** 绘图规范（字体、配色、导出、panel 信息架构、NMI Pastel 等），并将复杂投稿 figure 仍路由回该仓库的 `nature-figure` |
| **BioMini 绘图说明** | 工作流中的生信可视化指南（何时出图、Python/R 技术栈、色盲友好配色、标签防重叠、分层导出等），与本 Skill 的 `when-to-plot`、`backend-selection`、`export-policy` 等章节对应 |

在此基础上，作者根据自身生信分析场景做了以下定制：

- 范围收窄为 **单图 + 简单 2–4 panel**（patchwork/subplot），复杂 hero panel 投稿页交给 `nature-figure`
- **默认 Python**；仅在投稿/R/ComplexHeatmap 场景触发后端确认
- **communication / publication** 两档导出策略 + `scripts/qc.py` 自动质检
- 使用 **skill-creator** 流程建立 12 条行为 eval，iteration-2 达到 with_skill **100%** 通过率

感谢 [nature-skills](https://github.com/Yuan1z0825/nature-skills) 项目提供的优秀开源规范。

---

## 与 nature-skills 的分工

| 需求 | 使用 |
|------|------|
| 单张生信数据图、简单 2–4 panel 组合 | **本 Skill** |
| 复杂投稿 figure、hero panel、figure contract | [`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure) |
| 流程图、示意图、大段文字信息图 | Agent 的 **GenerateImage** |
| 论文润色、DA statement、PPT | nature-skills 中对应 skill |

---

## 安装

### Cursor / Claude Code

```bash
git clone https://github.com/Rooneyxu/bioinformatics-plotting-standards.git
# 任选其一
cp -R bioinformatics-plotting-standards ~/.cursor/skills/
cp -R bioinformatics-plotting-standards ~/.agents/skills/
```

重启 Agent 或新开对话后即可使用。

### 可选：User Rule（提高触发率）

```
涉及到生信相关的画图任务，使用 bioinformatics-plotting-standards skill。
```

### 依赖

```bash
pip install matplotlib seaborn pillow pandas numpy
# 仅在使用 R 后端时需要 R + ggplot2 / ComplexHeatmap 等
```

---

## 目录结构

```text
bioinformatics-plotting-standards/
├── SKILL.md                 # Agent 主规范（含 frontmatter 触发描述）
├── references/              # 模块化参考文档
│   ├── when-to-plot.md
│   ├── backend-selection.md
│   ├── export-policy.md
│   ├── color_schemes.md
│   ├── journal_requirements.md
│   └── troubleshooting.md
├── scripts/
│   └── qc.py                # 出图后 DPI / 格式 / 留白检查
└── evals/                   # skill-creator 行为与触发测试集
    ├── evals.json
    ├── trigger_eval.json
    └── grade_all_evals.py
```

---

## 快速使用

对 Agent 说例如：

```text
用 Python 画 DESeq2 火山图，padj<0.05 标 top15，组会预览 svg 即可
```

```text
scanpy UMAP + marker violin，简单 2-panel 横排，communication 档导出
```

出图后可用 QC 脚本检查：

```bash
python scripts/qc.py your_figure.png --mode communication
# 投稿场景
python scripts/qc.py your_figure.png --mode publication
```

---

## 许可证

MIT License — 见 [LICENSE](LICENSE)。

使用本 Skill 时，请同时遵守 [nature-skills](https://github.com/Yuan1z0825/nature-skills) 原项目的相关说明与署名习惯。

---

## 联系

- GitHub: [@Rooneyxu](https://github.com/Rooneyxu)
- Email: 1910305118@pku.edu.cn
