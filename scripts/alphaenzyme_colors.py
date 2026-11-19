#!/usr/bin/env python3
"""
AlphaEnzyme 风格配色（Liu et al., bioRxiv 2026.11.04.764416v2，从 Fig 1–5 实测提取）。

核心视觉配方：「80% 冷调钢青蓝单色阶 + 15% 暖杏沙色呼应 + 5% 焦糖橙点睛」。
特别适合计算方法学 Benchmark（多方法柱状图/箱线图/小提琴图）、单向相关性热图、
数据集队列单点高亮图以及双模态架构示意图。
"""

from __future__ import annotations

import matplotlib.colors as mcolors

# --- 1. 核心色板（80% 钢青蓝 + 15% 暖杏沙 + 5% 焦糖橙 + 卡片底色）---
ALPHAENZYME_CORE: dict[str, str] = {
    # 钢青蓝主阶（Hero 方法 & 序列/结构主模态）
    "hero_deep": "#195E8D",     # 深海钢蓝（热图高值 / 主角深强调）
    "hero_cobalt": "#2066AC",   # 钴钢蓝（队列单点高亮 / 关键柱体）
    "hero_main": "#316F98",     # 标准钢青蓝（本方法主力填充色）
    "teal_blue": "#5C98B6",     # 雾青蓝（次强变体 / 中高梯度）
    "mist_blue": "#90B6C9",     # 浅雾蓝（中等梯度 / 边框）
    "ice_slate": "#C3D6E0",     # 冰岩蓝（低值梯度 / 小提琴浅填充）
    # 暖杏沙对比阶（第二模态 / 次级对比项）
    "warm_sand": "#DBAE74",     # 暖沙金（Fig 2c 柱体暖对比色）
    "warm_apricot": "#EABB8E",  # 暖杏色（Fig 4/5 暖色柱体/模块）
    "peach_light": "#F4E3CF",   # 浅杏奶色（Fig 2d 小提琴浅填充 / 模块边框）
    # 5% 点睛强调色（仅用于 Top Hit / 关键突变 / 峰值标注）
    "callout_orange": "#D55E04",
    # 中性冷岩灰阶（Baseline 对照组）
    "gray_dark": "#7D8591",     # 最强 Baseline（深炭岩灰）
    "gray_mid": "#9199A3",      # 中等 Baseline
    "gray_soft": "#ADB4BC",     # 常规 Baseline
    "gray_light": "#CFD0D1",    # 浅灰 Baseline / 饼图背景扇区
    "gray_pale": "#E4E6E8",     # 极浅灰（最弱 Baseline / 网格）
    # 极淡分区底色与炭灰文字（去黑框、去死黑）
    "tint_ice": "#F0F5FB",      # 冰蓝卡片底衬（模态 A / 主架构容器）
    "tint_ice_sub": "#DBE9F6",  # 浅蓝子模块底衬
    "tint_peach": "#FCF0EA",    # 暖杏卡片底衬（模态 B / 化学或辅助输入）
    "tint_peach_sub": "#F9E0D1",# 浅杏子模块底衬
    "tint_panel": "#F6F7FA",    # 极淡冷灰画布/象限底衬
    "ink_dark": "#303030",      # 柔和深炭灰正文（替代死黑）
}

# --- 2. Fig 2c / 2d 风格：4–5 方法对比（3 冷灰 Baseline + 1 暖杏对比 + 1 主角钢蓝）---
# 适合分组柱状图、箱线图、小提琴图：用 1 个暖沙色打破多灰柱单调感，同时主角深蓝最醒目
ALPHAENZYME_FIG2C_BARS: list[str] = [
    "#B6B9C5",  # Baseline 1（浅紫灰）
    "#ACB3B2",  # Baseline 2（中冷灰）
    "#DBAE74",  # Baseline 3 / 特色对比法（暖沙金）
    "#8D9798",  # Baseline 4 / 强基线（深岩灰）
    "#316F98",  # Proposed Hero（深钢青蓝）
]

ALPHAENZYME_FIG2D_VIOLIN_FILLS: list[str] = [
    "#E6E8EC",  # Baseline 1 浅灰填充
    "#E3E5E7",  # Baseline 2 浅灰填充
    "#F4E3CF",  # Baseline 3 浅暖杏填充
    "#D9DFE4",  # Baseline 4 浅岩灰填充
    "#BFD2E2",  # Proposed Hero 浅冰蓝填充
]

ALPHAENZYME_FIG2D_VIOLIN_EDGES: list[str] = [
    "#9BA0AD",
    "#8E9697",
    "#C99658",
    "#6E797D",
    "#2C6C9B",
]

# --- 3. Fig 2e 风格：5–7 方法基准对比（全冷灰渐变阶梯 + 唯一主角钢蓝）---
# 极简克制：所有 Baseline 退居冷灰阶（由浅到深按性能排），全场仅本方法带彩色
ALPHAENZYME_FIG2E_MONO_BARS: list[str] = [
    "#E4E6E8",  # Weakest baseline
    "#D0D3D7",  # Baseline 2
    "#B9C0C8",  # Baseline 3
    "#9FA7B0",  # Baseline 4
    "#7D8591",  # Strongest baseline（深岩灰）
    "#2C6C9B",  # Proposed Hero（唯一彩色：深钢蓝）
]

# --- 4. Fig 2b 风格：数据集队列单点聚焦（全灰背景 + 唯一钴蓝主角）---
ALPHAENZYME_FIG2B_SPOTLIGHT: dict[str, str | list[str]] = {
    "spotlight": "#2066AC",
    "grays": ["#CFD0D1", "#B9C0C8", "#ADB4BC", "#9199A3", "#7D8591", "#E3E6EB"],
}

# --- 5. Fig 3f 风格：连续单向钢青蓝热图色带 ---
ALPHAENZYME_BLUE_RAMP: list[str] = [
    "#FDF8F4",  # 极淡暖白零值底
    "#DCEAF5",  # 浅冰蓝
    "#90B6C9",  # 雾蓝
    "#498CAE",  # 青蓝
    "#156089",  # 深海钢蓝
]

_CMAP_AE_BLUE: mcolors.LinearSegmentedColormap | None = None
_CMAP_AE_DIV: mcolors.LinearSegmentedColormap | None = None


def get_alphaenzyme_blue_cmap() -> mcolors.LinearSegmentedColormap:
    """单向连续钢青蓝 colormap（适合相关性、R²、AUC、Top-k 命中率热图）。"""
    global _CMAP_AE_BLUE
    if _CMAP_AE_BLUE is None:
        _CMAP_AE_BLUE = mcolors.LinearSegmentedColormap.from_list(
            "alphaenzyme_steel_blue",
            ALPHAENZYME_BLUE_RAMP,
            N=256,
        )
    return _CMAP_AE_BLUE


def get_alphaenzyme_diverging_cmap() -> mcolors.LinearSegmentedColormap:
    """钢青蓝 ↔ 暖杏橙发散 colormap（适合正负差值 Δ、双模态权重对比）。"""
    global _CMAP_AE_DIV
    if _CMAP_AE_DIV is None:
        _CMAP_AE_DIV = mcolors.LinearSegmentedColormap.from_list(
            "alphaenzyme_blue_apricot_div",
            ["#195E8D", "#6BA1BA", "#F7F8FA", "#EABB8E", "#D55E04"],
            N=256,
        )
    return _CMAP_AE_DIV


def get_mono_hero_palette(n_methods: int, hero_last: bool = True) -> list[str]:
    """生成 Fig 2e 风格色板：(n-1) 阶冷灰 Baseline + 1 个主角钢蓝 `#2C6C9B`。"""
    if n_methods <= 1:
        return ["#2C6C9B"]
    gray_cmap = mcolors.LinearSegmentedColormap.from_list(
        "_ae_gray", ["#E4E6E8", "#7D8591"]
    )
    n_base = n_methods - 1
    grays = [
        mcolors.to_hex(gray_cmap(i / max(1, n_base - 1)))
        for i in range(n_base)
    ]
    return grays + ["#2C6C9B"] if hero_last else ["#2C6C9B"] + grays
