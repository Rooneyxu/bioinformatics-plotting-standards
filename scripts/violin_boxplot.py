#!/usr/bin/env python3
"""
Li Lab 风格：小提琴图 + 箱线图叠画。

推荐用 matplotlib 在同一 ax 上先 violinplot 再 boxplot（位置对齐最稳）。
配色见 references/color_schemes.md「Li Lab violin+box」与 references/violin-boxplot.md。

用法：
    python scripts/violin_boxplot.py --demo grouped
    python scripts/violin_boxplot.py --demo paired --output /tmp/demo.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np

# --- Li Lab 配色常量（与 lilab_plot_code 一致）---

PALETTE_LILAB_PAIR = {
    "violin_fill": ["#DDC4E0", "#E9E9E9"],
    "box_edge": ["#A362AC", "#BEBEBE"],
    "box_face": "#FFFFFF",
    "ref_line": "#7F7F7F",
}

PALETTE_LILAB_TRIPLE = {
    "violin_fill": ["#DDC4E0", "#FFD4AB", "#E9E9E9"],
    "box_edge": ["#984EA3", "#FF7F00", "#BEBEBE"],
    "box_face": ["#F1E6F2", "#FAE9D8", "#F6F6F6"],
    "ref_line": "#7F7F7F",
}

PaletteName = Literal["pair", "triple"]


def get_lilab_palette(name: PaletteName) -> dict:
    """返回 Li Lab 小提琴+箱线配色字典。name 为 pair（两组交替）或 triple（三组）。"""
    if name == "pair":
        return PALETTE_LILAB_PAIR
    if name == "triple":
        return PALETTE_LILAB_TRIPLE
    raise ValueError(f"未知 palette: {name}，请用 pair 或 triple")


def _pick_color(colors: str | Sequence[str], index: int) -> str:
    """从单色或列表中按索引取色（循环）。"""
    if isinstance(colors, str):
        return colors
    return colors[index % len(colors)]


def _style_violin_bodies(violin_bodies, palette: dict, n_colors: int) -> None:
    """为小提琴 collections 上色。"""
    fills = palette["violin_fill"]
    for i, body in enumerate(violin_bodies):
        body.set_facecolor(_pick_color(fills, i % n_colors))
        body.set_edgecolor(None)
        body.set_linewidth(0.1)
        body.set_alpha(1.0)


def _style_boxplot_elements(boxes: dict, palette: dict, n_colors: int) -> None:
    """为 boxplot 返回 dict 中的 boxes/whiskers/medians/fliers 上色。"""
    edge_colors = palette["box_edge"]
    face_colors = palette.get("box_face", "#FFFFFF")

    for i, box in enumerate(boxes["boxes"]):
        box.set_edgecolor(_pick_color(edge_colors, i % n_colors))
        box.set_facecolor(_pick_color(face_colors, i % n_colors))

    for i, whisker in enumerate(boxes["whiskers"]):
        group_idx = i // 2
        whisker.set_color(_pick_color(edge_colors, group_idx % n_colors))
        whisker.set_linewidth(0.75)

    for i, median in enumerate(boxes["medians"]):
        median.set_color(_pick_color(edge_colors, i % n_colors))
        median.set_linewidth(1.5)
        median.set_solid_capstyle("butt")

    for i, flier in enumerate(boxes["fliers"]):
        c = _pick_color(edge_colors, i % n_colors)
        flier.set_markeredgecolor(c)
        flier.set_markerfacecolor(c)
        flier.set_markersize(2.0)


def plot_violin_box(
    data_list: Sequence[Sequence[float]],
    positions: Sequence[float],
    *,
    ax: plt.Axes | None = None,
    palette: PaletteName = "pair",
    color_indices: Sequence[int] | None = None,
    violin_width: float = 1.0,
    box_width: float | None = None,
    bw_method: str | float = "silverman",
    show_caps: bool = False,
    show_fliers: bool = True,
    ref_lines: Iterable[float] | None = None,
    ylabel: str = "value",
    figsize: tuple[float, float] = (3.2, 2.8),
) -> tuple[plt.Figure, plt.Axes]:
    """
    matplotlib 叠画：先小提琴、后箱线，共用 positions。

    参数:
        data_list: 每组一列数值，长度须与 positions 相同。
        positions: 每组 x 轴位置（可非等距，用于成对并排布局）。
        palette: pair（紫/灰交替）或 triple（紫/橙/灰）。
        color_indices: 每组用 palette 中第几色；默认 0,1,0,1,...（pair）或 0,1,2,0,1,2,...（triple）。
        ref_lines: 可选水平参考线 y 值列表。
        返回: (fig, ax)
    """
    if len(data_list) != len(positions):
        raise ValueError("data_list 与 positions 长度须一致")

    pal = get_lilab_palette(palette)
    n_palette = 2 if palette == "pair" else 3

    if color_indices is None:
        color_indices = [i % n_palette for i in range(len(data_list))]

    own_fig = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    else:
        fig = ax.figure

    if ref_lines is not None:
        for y in ref_lines:
            ax.axhline(y, color=pal.get("ref_line", "#7F7F7F"), alpha=0.5, linewidth=0.1)

    violins = ax.violinplot(
        dataset=list(data_list),
        positions=list(positions),
        widths=violin_width,
        bw_method=bw_method,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for i, body in enumerate(violins["bodies"]):
        idx = color_indices[i] % n_palette
        fills = pal["violin_fill"]
        body.set_facecolor(_pick_color(fills, idx))
        body.set_edgecolor(None)
        body.set_linewidth(0.1)
        body.set_alpha(1.0)

    medianprops = dict(linewidth=1.5, solid_capstyle="butt")
    boxprops = dict(linewidth=0.75, facecolor="white")
    whiskerprops = dict(linewidth=0.75)

    boxes = ax.boxplot(
        list(data_list),
        positions=list(positions),
        widths=box_width,
        showfliers=show_fliers,
        showcaps=show_caps,
        patch_artist=True,
        medianprops=medianprops,
        whiskerprops=whiskerprops,
        boxprops=boxprops,
        flierprops={"markersize": 0.3, "marker": "o"},
    )

    edge_colors = pal["box_edge"]
    face_colors = pal.get("box_face", "#FFFFFF")
    for i, box in enumerate(boxes["boxes"]):
        idx = color_indices[i] % n_palette
        box.set_edgecolor(_pick_color(edge_colors, idx))
        box.set_facecolor(_pick_color(face_colors, idx))

    for i, whisker in enumerate(boxes["whiskers"]):
        group_idx = i // 2
        idx = color_indices[group_idx] % n_palette
        whisker.set_color(_pick_color(edge_colors, idx))

    for i, median in enumerate(boxes["medians"]):
        idx = color_indices[i] % n_palette
        median.set_color(_pick_color(edge_colors, idx))

    for i, flier in enumerate(boxes["fliers"]):
        idx = color_indices[i] % n_palette
        c = _pick_color(edge_colors, idx)
        flier.set_markeredgecolor(c)
        flier.set_markerfacecolor(c)

    ax.set_ylabel(ylabel, fontsize=8, fontweight="bold")
    sns_despine_compat(ax)

    if own_fig:
        return fig, ax
    return fig, ax


def plot_violin_box_grouped(
    df,
    *,
    x: str,
    y: str,
    order: Sequence[str] | None = None,
    ax: plt.Axes | None = None,
    palette: PaletteName = "triple",
    violin_width: float = 0.35,
    figsize: tuple[float, float] = (4.0, 3.0),
) -> tuple[plt.Figure, plt.Axes]:
    """
    长表 DataFrame：每组一列位置 0,1,2,...，适合 2–3 组标准分类轴。

    仍用 matplotlib 叠画（不用 seaborn 双图层），避免须线索引脆弱问题。
    """
    import pandas as pd

    if order is None:
        order = list(df[x].dropna().unique())
    data_list = [df.loc[df[x] == g, y].dropna().values for g in order]
    positions = list(range(len(order)))
    color_indices = list(range(len(order)))

    own_fig = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    else:
        fig = ax.figure

    plot_violin_box(
        data_list,
        positions,
        ax=ax,
        palette=palette,
        color_indices=color_indices,
        violin_width=violin_width,
        ylabel=y,
    )
    ax.set_xticks(positions)
    ax.set_xticklabels(order, fontsize=7)
    ax.set_xlabel("")

    if own_fig:
        return fig, ax
    return fig, ax


def sns_despine_compat(ax: plt.Axes) -> None:
    """去掉上/右边框，与 skill 默认 ticks 风格一致。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _demo_paired(output: Path | None) -> None:
    """成对并排布局 demo（复现 lilab SUMOSIM 风格）。"""
    rng = np.random.default_rng(0)
    data_list = [
        rng.normal(2, 2, 40),
        rng.normal(0, 1.5, 40),
        rng.normal(5, 2, 40),
        rng.normal(3, 1.5, 40),
    ]
    base = [-0.5, 0.5, 2.5, 3.5]
    positions = [b + 2 for b in base]

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["svg.fonttype"] = "none"
    fig, ax = plot_violin_box(
        data_list,
        positions,
        palette="pair",
        color_indices=[0, 1, 0, 1],
        ref_lines=[-5, 0, 5, 10],
        figsize=(2.5, 1.2),
        ylabel="value",
    )
    ax.set_xticks([2, 5])
    ax.set_xticklabels(["Condition A", "Condition B"], fontsize=6)
    ax.tick_params(labelsize=5)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=600, bbox_inches="tight")
        print(f"Saved: {output}")
    plt.close(fig)


def _demo_grouped(output: Path | None) -> None:
    """三组标准分类轴 demo。"""
    import pandas as pd

    rng = np.random.default_rng(1)
    df = pd.DataFrame({
        "Group": ["G1"] * 30 + ["G2"] * 30 + ["G3"] * 30,
        "score": np.concatenate([
            rng.normal(0.7, 0.1, 30),
            rng.normal(0.85, 0.08, 30),
            rng.normal(0.6, 0.12, 30),
        ]),
    })

    plt.rcParams["font.family"] = "Arial"
    fig, ax = plot_violin_box_grouped(df, x="Group", y="score", palette="triple")
    ax.set_ylabel("Predict score", fontsize=8, fontweight="bold")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=300, bbox_inches="tight")
        print(f"Saved: {output}")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Li Lab violin + box overlay plots")
    parser.add_argument("--demo", choices=["paired", "grouped"], help="运行内置示例")
    parser.add_argument("--output", type=Path, help="示例图保存路径")
    args = parser.parse_args()

    if args.demo == "paired":
        _demo_paired(args.output)
    elif args.demo == "grouped":
        _demo_grouped(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
