#!/usr/bin/env python3
"""
Nature AD 2024 风格配色（Green et al., Nature 633, 2024）。

参考：lilab_plot_code/配色.pdf 与课题 PPT；用于发散热图、UMAP 亚群、顺序紫条等。
Li Lab violin+box 分类色仍用 violin_boxplot.py 的 pair/triple，与此模块互补。
"""

from __future__ import annotations

import matplotlib.colors as mcolors

# --- 发散：紫（负）→ 白 → 绿（正），Fig.1c cognitive decline / z-score ---
NATURE_PG_NEG = "#7B3294"
NATURE_PG_MID = "#FFFFFF"
NATURE_PG_POS = "#008837"

# --- 顺序紫：Fig.1b 分类计数条 ---
NATURE_SEQ_PURPLE = ["#E7D4E8", "#C2A5CF", "#A17CB4", "#8B5A9F", "#762A83"]

# --- 棕色系：UMAP 小胶质细胞等（Mic.12/13 赤褐、Mic.15 褐紫）---
NATURE_BROWN_TERRACOTTA = "#8C564B"   # 主棕色，用户偏好
NATURE_BROWN_GOLD = "#BF812D"
NATURE_BROWN_TAN = "#C49C94"
NATURE_BROWN_MAUVE = "#9970AB"        # 褐紫色 Mic.15

# --- 多类别定性色（UMAP / 细胞亚群，含棕）---
QUALITATIVE_NATURE_AD2024 = [
    "#762A83",  # 深紫 Mic.7
    "#008837",  # 森林绿 Mic.9
    NATURE_BROWN_TERRACOTTA,  # 赤褐 Mic.12/13
    "#016FAF",  # 海军蓝 Mic.1/16
    "#5AAE61",  # 鼠尾草绿 Mic.3–5
    "#C2A5CF",  # 薰衣草 Mic.6/10/11
    NATURE_BROWN_GOLD,
    "#87CEEB",  # 天蓝 Monocytes
    NATURE_BROWN_MAUVE,
    "#A6D96A",  # 黄绿 Mic.2
    "#9467BD",  # 长春花紫 Macrophages
    "#E7D4E8",  # 浅紫
]

_CMAP_DIVERGING_PG: mcolors.LinearSegmentedColormap | None = None
_CMAP_SEQ_PURPLE: mcolors.LinearSegmentedColormap | None = None


def get_diverging_cmap() -> mcolors.LinearSegmentedColormap:
    """紫–白–绿发散 colormap（替代 RdBu_r 的 Nature 风格默认）。"""
    global _CMAP_DIVERGING_PG
    if _CMAP_DIVERGING_PG is None:
        _CMAP_DIVERGING_PG = mcolors.LinearSegmentedColormap.from_list(
            "nature_ad2024_purple_green",
            [NATURE_PG_NEG, NATURE_PG_MID, NATURE_PG_POS],
            N=256,
        )
    return _CMAP_DIVERGING_PG


def get_sequential_purple_cmap() -> mcolors.LinearSegmentedColormap:
    """浅紫→深紫顺序 colormap（分类计数、单变量强度）。"""
    global _CMAP_SEQ_PURPLE
    if _CMAP_SEQ_PURPLE is None:
        _CMAP_SEQ_PURPLE = mcolors.LinearSegmentedColormap.from_list(
            "nature_ad2024_seq_purple",
            NATURE_SEQ_PURPLE,
            N=256,
        )
    return _CMAP_SEQ_PURPLE


def qualitative_palette(n: int) -> list[str]:
    """取前 n 个 Nature AD2024 定性色（循环）。"""
    if n <= 0:
        return []
    base = QUALITATIVE_NATURE_AD2024
    return [base[i % len(base)] for i in range(n)]
