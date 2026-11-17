#!/usr/bin/env python3
"""
学位论文统一绘图样式与面板编号工具（PKU Thesis Style）。

核心约束（北京大学学位论文规范 + 扁平 7.5 pt 统一字号体系）：
1. 画布物理宽度不超过 A4 竖排净版心 15.80 cm (6.22 in = 448 pt)，按内容自由设定宽度（<= 6.20 in）并 100% 原大插入 Word/LaTeX 免缩放；内置三档常用参考预设：
   - full   (通栏参考): 6.20 in (15.75 cm)
   - medium (中等参考): 4.20 in (10.67 cm)
   - half   (半栏参考): 3.00 in (7.62 cm)
2. 扁平化字号阶梯（全员严格 <= 五号字 10.5 pt，跨图高度一致）：
   - 组图面板字母 A, B, C, D : 10.0 pt Arial Bold（大写）
   - 子图标题 (Panel Title)  : 8.5 pt Arial Bold
   - 坐标轴标题 / 刻度 / 图例 / 图内常规注释 : 统一 7.5 pt（六号字，常规字重）
   - 超密标注特例下限        : 6.5 pt（绝对硬下限 6.0 pt）
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# 1:1 物理宽度档位（单位：英寸；对应 A4 左右页边距 2.60 cm 后的净版心 15.80 cm = 6.22 in）
THESIS_WIDTHS_IN: dict[str, float] = {
    "full": 6.20,    # 15.75 cm — 通栏多面板组图、宽幅热图/Funkyheatmap
    "medium": 4.20,  # 10.67 cm — 标准单图居中展示
    "half": 3.00,    # 7.62 cm  — 紧凑单图或两张单图左右并排
}

# 扁平 7.5 pt 字号常量（单位：pt；五号字红线为 10.5 pt）
THESIS_FONT_SIZES: dict[str, float] = {
    "panel_label": 10.0,  # 大写 A, B, C, D（Arial Bold）
    "title": 8.5,         # 子图标题（Arial Bold）
    "body": 7.5,          # 坐标轴标题、刻度数字、图例、常规图内注释统一 7.5 pt（六号字）
    "dense_min": 6.5,     # 密集基因名/数值标注特例
    "hard_ceiling": 10.5, # 五号字硬上限
}

# 多条曲线区分用点型序列（满足学位论文黑白打印/缩微可分辨要求）
THESIS_MARKERS: list[str] = ["o", "s", "^", "D", "v", "P"]

THESIS_FONT_STACK: list[str] = ["Arial", "Helvetica", "SimHei", "Noto Sans CJK JP", "DejaVu Sans"]


def apply_thesis_style() -> dict[str, float]:
    """初始化 matplotlib/seaborn 全局参数为毕业论文扁平 7.5 pt 规范。"""
    sns.set_theme(style="ticks")
    body_pt = THESIS_FONT_SIZES["body"]
    title_pt = THESIS_FONT_SIZES["title"]

    mpl.rcParams.update({
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.family": "sans-serif",
        "font.sans-serif": THESIS_FONT_STACK,
        "font.size": body_pt,
        "axes.titlesize": title_pt,
        "axes.titleweight": "bold",
        "axes.labelsize": body_pt,
        "axes.labelweight": "normal",
        "xtick.labelsize": body_pt,
        "ytick.labelsize": body_pt,
        "legend.fontsize": body_pt,
        "legend.title_fontsize": body_pt,
        "legend.frameon": False,
        "figure.titlesize": title_pt,
        "figure.titleweight": "bold",
        "axes.linewidth": 0.75,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "xtick.direction": "out",
        "ytick.direction": "out",
    })
    return dict(THESIS_FONT_SIZES)


def create_thesis_figure(
    width_tier: str = "medium",
    height_in: float = 3.2,
    width_in: float | None = None,
    nrows: int = 1,
    ncols: int = 1,
    w_pad: float = 0.06,
    h_pad: float = 0.06,
    wspace: float = 0.05,
    hspace: float = 0.07,
    **subplot_kw,
):
    """创建毕业论文画布：可传任意自定义 width_in（建议 <= 6.20 in），或使用 width_tier 参考预设。"""
    apply_thesis_style()
    if width_in is None:
        if width_tier not in THESIS_WIDTHS_IN:
            raise ValueError(f"width_tier must be one of {tuple(THESIS_WIDTHS_IN)}, got {width_tier!r}")
        width_in = THESIS_WIDTHS_IN[width_tier]
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(width_in, height_in),
        layout="constrained",
        **subplot_kw,
    )
    engine = fig.get_layout_engine()
    if engine is not None:
        engine.set(w_pad=w_pad, h_pad=h_pad, wspace=wspace, hspace=hspace)
    return fig, axes


def add_panel_labels(
    fig: plt.Figure,
    axes: Sequence[plt.Axes],
    labels: Iterable[str] | None = None,
    dx_pt: float = -28.0,
    dy_pt: float = 6.0,
) -> list[plt.Text]:
    """
    在多面板组图左上角添加统一的大写粗体面板字母（A, B, C, D...，固定 10.0 pt Arial Bold）。

    同一列自动对齐最左轴偏移，同一行（y1 相差 < 12 pt）自动对齐最高轴顶，保证视觉严格齐平。
    """
    fig.canvas.draw()
    fig_w_pt = fig.get_figwidth() * 72.0
    fig_h_pt = fig.get_figheight() * 72.0

    if labels is None:
        labels = [chr(ord("A") + i) for i in range(len(axes))]
    label_list = [str(lbl).strip().upper() for lbl in labels]

    bboxes = [ax.get_position() for ax in axes]
    raw_xs = [max(0.006, b.x0 + dx_pt / fig_w_pt) for b in bboxes]
    raw_ys = [min(0.975, b.y1 + dy_pt / fig_h_pt) for b in bboxes]

    # 对相近列与相近行做吸附对齐（容差 12 pt）
    tol_x = 12.0 / fig_w_pt
    tol_y = 12.0 / fig_h_pt
    aligned_xs = list(raw_xs)
    aligned_ys = list(raw_ys)
    for i in range(len(axes)):
        near_x = [raw_xs[j] for j in range(len(axes)) if abs(raw_xs[j] - raw_xs[i]) <= tol_x]
        near_y = [raw_ys[j] for j in range(len(axes)) if abs(raw_ys[j] - raw_ys[i]) <= tol_y]
        aligned_xs[i] = min(near_x)
        aligned_ys[i] = max(near_y)

    texts: list[plt.Text] = []
    for x, y, ch in zip(aligned_xs, aligned_ys, label_list):
        t = fig.text(
            x,
            y,
            ch,
            fontsize=THESIS_FONT_SIZES["panel_label"],
            fontweight="bold",
            fontfamily="Arial",
            ha="left",
            va="bottom",
            color="#000000",
        )
        texts.append(t)
    return texts


def format_stat_p(p_val: float, symbol: str = "p") -> str:
    """格式化显著性标注，强制统计符号 p 使用斜体（符合北大学位论文模板要求）。"""
    if p_val < 1e-4:
        return rf"$\it{{{symbol}}}$ = {p_val:.1e}"
    if p_val < 0.001:
        return rf"$\it{{{symbol}}}$ = {p_val:.4f}"
    return rf"$\it{{{symbol}}}$ = {p_val:.3f}"


def strip_meaningless_ticks(ax: plt.Axes) -> None:
    """对 UMAP / t-SNE / 空间原位图等无物理量纲坐标轴移除刻度线与细小数字。"""
    ax.set_xticks([])
    ax.set_yticks([])


def save_thesis_figure(
    fig: plt.Figure,
    output_stem: str | Path,
    dpi: int = 600,
    bbox_inches: str | None = "tight",
    close: bool = True,
) -> Path:
    """导出 PNG (600 DPI) + PDF + SVG（插入 Word 保持 100% 原始尺寸即可保证全文字号一致）。"""
    stem = Path(output_stem)
    if stem.suffix.lower() in {".png", ".pdf", ".svg"}:
        stem = stem.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(stem.with_suffix(".png"), dpi=dpi, bbox_inches=bbox_inches)
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches=bbox_inches)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches=bbox_inches)
    if close:
        plt.close(fig)
    return stem.with_suffix(".png")
