# 热图列分组注释

带样本/条件分组的热图，底部注释**必须用独立 axes**，不要在热图 axes 上叠 `Rectangle` + `ax.text` + `xlabel`。

## 反模式（勿用）

```python
# ❌ 在热图 transData 坐标外手绘色条 + 组名，再 set_xlabel("Sample")
# → Control / Sample / AD 挤在同一行，视觉重复
for i, color in enumerate(col_color_list):
    ax.add_patch(plt.Rectangle((i, n_genes), 1, 0.4, clip_on=False, ...))
ax.text(0.5, n_genes + 0.55, "Control", transform=ax.transData, ...)
ax.set_xlabel("Sample")
```

原因：`clip_on=False` 与 `constrained_layout` / `bbox_inches="tight"` 争空间，手写文字与 matplotlib 自动 xlabel 重叠。

## 推荐：GridSpec 分轴

```python
from scripts.heatmap_annotation import plot_heatmap_with_col_groups
from scripts.nature_ad2024_colors import get_diverging_cmap

group_colors = {"Control": "#BEBEBE", "AD": "#A362AC"}
col_groups = ["Control"] * 4 + ["AD"] * 4  # 每列一个分组名

fig, ax_heat, ax_ann = plot_heatmap_with_col_groups(
    zscore_df,
    col_groups,
    group_colors,
    cmap=get_diverging_cmap(),
    center=0,
    vmin=-3,
    vmax=3,
    title="Top DEG expression",
    ylabel="Gene",
)
# 勿再 ax.set_xlabel("Sample") — 底部分组色条已说明列分组
fig.savefig("heatmap.png", dpi=300, bbox_inches="tight")
plt.close(fig)
```

## 规则

| 项 | 做法 |
|---|---|
| 列分组 | 底部分组色条 + 组名居中写在色块内 |
| x 轴标题 | **省略**；或仅在没有分组条时写 `Condition` |
| 样本 ID | 默认隐藏（`xticklabels=False`）；需要时在色条上方加第二行细标签 |
| 复杂多层注释 | R → ComplexHeatmap；Python 可考虑 `seaborn.clustermap(col_colors=...)` |

## 相关

- 发散配色：[color_schemes.md](color_schemes.md)
- 底部分组叠字：[troubleshooting.md](troubleshooting.md#热图底部分组注释重叠)
