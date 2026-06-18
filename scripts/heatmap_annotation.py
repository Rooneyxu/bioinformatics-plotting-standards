#!/usr/bin/env python3
"""
热图底部分组列注释（matplotlib + seaborn）。

用独立 annotation axes 画分组色条，避免在热图 axes 上用 transData + clip_on=False
导致与 xlabel 重叠、文字重复。

用法见 references/heatmap-annotation.md
"""

from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def _group_spans(labels: Sequence[str]) -> list[tuple[int, int, str]]:
    """连续相同分组 → (start_col, end_col, group_name)，end 为开区间。"""
    if not labels:
        return []
    spans: list[tuple[int, int, str]] = []
    start = 0
    current = labels[0]
    for i in range(1, len(labels)):
        if labels[i] != current:
            spans.append((start, i, current))
            start = i
            current = labels[i]
    spans.append((start, len(labels), current))
    return spans


def add_column_group_bar(
    ax_ann: Axes,
    col_groups: Sequence[str],
    group_colors: Mapping[str, str],
    *,
    bar_height: float = 0.75,
    label_fontsize: float = 6,
    label_color: str = "#333333",
) -> None:
    """
    在专用 annotation axes 上绘制列分组色条与组名（每组一段，不重复写 xlabel）。

    参数:
        ax_ann: 热图下方的窄 axes，x 范围须与热图列数一致 [0, n_cols]。
        col_groups: 每列对应的分组名，长度 = 列数。
        group_colors: 分组名 → 填充色。
    """
    n_cols = len(col_groups)
    ax_ann.set_xlim(0, n_cols)
    ax_ann.set_ylim(0, 1)
    ax_ann.axis("off")

    y_center = 0.5
    for start, end, group in _group_spans(col_groups):
        width = end - start
        color = group_colors.get(group, "#CCCCCC")
        ax_ann.barh(
            y_center,
            width,
            left=start,
            height=bar_height,
            color=color,
            align="center",
            edgecolor="none",
        )
        ax_ann.text(
            start + width / 2,
            y_center,
            group,
            ha="center",
            va="center",
            fontsize=label_fontsize,
            color=label_color,
            clip_on=False,
        )


def plot_heatmap_with_col_groups(
    data: pd.DataFrame,
    col_groups: Sequence[str],
    group_colors: Mapping[str, str],
    *,
    cmap,
    center: float | None = 0,
    vmin: float | None = None,
    vmax: float | None = None,
    cbar_label: str = "Z-score",
    title: str | None = None,
    ylabel: str = "Gene",
    italic_row_labels: bool = True,
    figsize: tuple[float, float] = (3.6, 3.8),
    ann_height_ratio: float = 0.06,
    heatmap_kws: dict | None = None,
) -> tuple[Figure, Axes, Axes]:
    """
    热图 + 底部分组色条（GridSpec 分轴，避免注释与 xlabel 叠字）。

    参数:
        data: 行=特征、列=样本的矩阵（DataFrame）。
        col_groups: 与 data.columns 等长的分组标签。
        group_colors: 分组配色。
        返回: (fig, ax_heat, ax_ann)
    """
    if len(col_groups) != data.shape[1]:
        raise ValueError("col_groups 长度须等于 data 列数")

    heatmap_kws = heatmap_kws or {}
    n_ann = max(ann_height_ratio, 0.04)
    n_heat = 1.0 - n_ann

    fig = plt.figure(figsize=figsize, constrained_layout=True)
    gs = GridSpec(
        2,
        2,
        figure=fig,
        height_ratios=[n_heat, n_ann],
        width_ratios=[1.0, 0.06],
        hspace=0.06,
        wspace=0.05,
    )
    ax_heat = fig.add_subplot(gs[0, 0])
    ax_cbar = fig.add_subplot(gs[0, 1])
    ax_ann = fig.add_subplot(gs[1, 0], sharex=ax_heat)

    sns.heatmap(
        data,
        ax=ax_heat,
        cbar_ax=ax_cbar,
        cmap=cmap,
        center=center,
        vmin=vmin,
        vmax=vmax,
        linewidths=heatmap_kws.pop("linewidths", 0.3),
        linecolor=heatmap_kws.pop("linecolor", "#F0F0F0"),
        xticklabels=heatmap_kws.pop("xticklabels", False),
        yticklabels=heatmap_kws.pop("yticklabels", True),
        cbar_kws=heatmap_kws.pop("cbar_kws", {"label": cbar_label}),
        **heatmap_kws,
    )

    if title:
        ax_heat.set_title(title, fontsize=9, fontweight="bold")
    ax_heat.set_ylabel(ylabel, fontsize=8, fontweight="bold")
    ax_heat.set_xlabel("")  # 分组色条已表达列信息，勿再写 Sample/Condition
    ax_heat.tick_params(axis="y", labelsize=6)

    if italic_row_labels:
        for tick in ax_heat.get_yticklabels():
            tick.set_fontstyle("italic")

    add_column_group_bar(ax_ann, col_groups, group_colors)

    cbar = ax_heat.collections[0].colorbar
    cbar.ax.tick_params(labelsize=6)
    cbar.set_label(cbar_label, fontsize=7, fontweight="bold")

    return fig, ax_heat, ax_ann
