#!/usr/bin/env python3
"""
图表质量检查脚本。
保存图表后运行，验证 DPI、尺寸、空白率、矢量格式是否齐全；
在 `--mode thesis`（毕业论文规范）下额外解析 PDF 内真实物理字号与面板字母一致性：
  - [FAIL] 阻断项：文字超过 10.5 pt（五号字红线）或低于 5.5 pt、误用小写面板标签（a, b, c）、多面板 A/B/C/D 字体/字号不一致、误用 M/mM/μM 浓度单位；
  - [WARN] 提醒项：画布宽度 > 6.22 in（15.80 cm A4 竖排净版心），提醒插入竖排页会被 Word 自动缩小（若用于横排页可忽略）。

用法：
    python scripts/qc.py figure_name.png --mode thesis
    python scripts/qc.py figure_name.png --mode publication
    python scripts/qc.py figure_name.png --mode communication
    python scripts/qc.py output/ --mode thesis
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THESIS_MAX_WIDTH_IN = 6.25      # 北大 A4 净版心 15.80 cm = 6.22 in，留 0.03 in 浮点容差
THESIS_MAX_FONT_PT = 10.55      # 五号字 10.5 pt 上限（含 0.05 pt 浮点容差）
THESIS_MIN_FONT_PT = 5.45       # 可读性硬下限 5.5 pt


def _audit_thesis_pdf_typography(pdf_path: Path) -> tuple[list[str], list[str]]:
    """用 PyMuPDF 检查毕业论文 PDF 的字号红线（<=10.5pt）、面板字母一致性与版心宽度提醒。"""
    issues: list[str] = []
    warnings: list[str] = []
    try:
        import pymupdf
    except ImportError:
        return ["PyMuPDF (pymupdf) not installed — cannot verify thesis PDF font sizes"], warnings

    doc = pymupdf.open(pdf_path)
    if len(doc) == 0:
        doc.close()
        return ["Empty PDF file"], warnings

    page = doc[0]
    w_in = page.rect.width / 72.0
    if w_in > THESIS_MAX_WIDTH_IN:
        shrink_pct = (6.22 / w_in) * 100.0
        warnings.append(
            f"Canvas width {w_in:.2f} in ({w_in * 2.54:.2f} cm) > 6.22 in (15.80 cm portrait text block); "
            f"Word will shrink fonts to {shrink_pct:.0f}% (7.5 pt -> {7.5 * 6.22 / w_in:.1f} pt) unless placed on a landscape page"
        )

    over_ceiling: list[str] = []
    under_floor: list[str] = []
    molar_unit_violations: list[str] = []
    upper_panel_tags: list[tuple[str, str, float]] = []  # (letter, font, size_pt)
    lower_panel_suspects: list[tuple[str, float]] = []
    molar_re = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?\s*(?:mM|uM|μM|µM|nM|pM|M)(?![A-Za-z0-9])")

    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        lines = block.get("lines", [])

        for ln in lines:
            line_text = "".join(s.get("text", "") for s in ln.get("spans", [])).strip()
            if molar_re.search(line_text):
                molar_unit_violations.append(line_text[:30])
            for sp in ln.get("spans", []):
                txt = sp.get("text", "").strip()
                if not txt:
                    continue
                raw_sz = float(sp.get("size", 0.0))
                font_name = sp.get("font", "")

                if raw_sz > THESIS_MAX_FONT_PT:
                    over_ceiling.append(f"'{txt[:20]}' ({raw_sz:.2f} pt > 10.5 pt Wuhao)")
                elif raw_sz < THESIS_MIN_FONT_PT:
                    # 忽略纯数学上下标单字符（如 10^-9 中的 -9）
                    if len(txt) > 2 or not re.match(r"^[-+0-9]+$", txt):
                        under_floor.append(f"'{txt[:20]}' ({raw_sz:.2f} pt < 5.5 pt)")

                # 识别独立的单字母面板标签候选（注意同行 A 和 B 可能被 PyMuPDF 归入同一 block 的不同 span/line）
                is_bold = "bold" in font_name.lower() or bool(sp.get("flags", 0) & 16)
                if len(txt) == 1 and txt.isalpha() and (len(line_text) == 1 or is_bold):
                    if txt in "ABCDEFGHIJKLMNOP" and (raw_sz >= 8.8 or is_bold):
                        upper_panel_tags.append((txt, font_name, round(raw_sz, 2)))
                    elif txt in "abcdefghijklmnop" and is_bold and raw_sz >= 7.5:
                        lower_panel_suspects.append((txt, round(raw_sz, 2)))

    doc.close()

    if over_ceiling:
        sample = "; ".join(over_ceiling[:5])
        issues.append(f"Font size exceeds Wuhao (10.5 pt): {sample}")
    if under_floor:
        sample = "; ".join(under_floor[:5])
        issues.append(f"Font size too small (< 5.5 pt): {sample}")

    if lower_panel_suspects and not upper_panel_tags:
        letters = ", ".join(f"'{c}' ({sz}pt)" for c, sz in lower_panel_suspects)
        issues.append(
            f"Lowercase panel labels detected ({letters}) — thesis requires UPPERCASE A, B, C, D!"
        )

    if len(upper_panel_tags) >= 2:
        fonts = {re.sub(r"^[A-Z]{6}\+", "", f) for _, f, _ in upper_panel_tags}
        sizes = [sz for _, _, sz in upper_panel_tags]
        if len(fonts) > 1:
            issues.append(f"Inconsistent panel label fonts across A/B/C/D: {sorted(fonts)}")
        if max(sizes) - min(sizes) > 0.25:
            issues.append(f"Inconsistent panel label sizes across A/B/C/D: {upper_panel_tags}")

    if molar_unit_violations:
        sample = "; ".join(dict.fromkeys(molar_unit_violations))
        issues.append(
            f"Molarity unit 'M/mM/μM' detected ({sample}) — PKU thesis requires 'mol/L' (mmol/L, μmol/L) with a space after the number!"
        )

    return issues, warnings


def check_figure_quality(
    png_path: str,
    min_dpi: int = 600,
    require_pdf: bool = True,
    mode: str = "thesis",
) -> dict:
    """
    检查保存的图表质量。
    返回检查结果字典，包含通过/失败状态和详细信息。
    """
    from PIL import Image
    import numpy as np

    png_path_obj = Path(png_path)
    results: dict = {"path": str(png_path_obj), "passed": True, "issues": [], "warnings": []}

    # 1. 文件存在性检查
    if not png_path_obj.exists():
        results["passed"] = False
        results["issues"].append(f"File not found: {png_path_obj}")
        return results

    # 2. 文件大小检查（过小可能是空白图）
    file_size_kb = png_path_obj.stat().st_size / 1024
    if file_size_kb < 10:
        results["passed"] = False
        results["issues"].append(f"File too small ({file_size_kb:.1f} KB) — likely blank")

    # 3. 分辨率检查
    img = Image.open(png_path_obj)
    width_px, height_px = img.size
    dpi_info = img.info.get("dpi", (72, 72))
    actual_dpi = dpi_info[0] if isinstance(dpi_info, tuple) else dpi_info

    if actual_dpi < min_dpi - 1:
        results["issues"].append(f"DPI too low: {actual_dpi:.0f} (expected >= {min_dpi})")

    # 4. 尺寸合理性检查
    width_inches = width_px / actual_dpi if actual_dpi > 0 else 0
    height_inches = height_px / actual_dpi if actual_dpi > 0 else 0
    if mode == "thesis" and width_inches > THESIS_MAX_WIDTH_IN and not png_path_obj.with_suffix(".pdf").exists():
        results["warnings"].append(
            f"Canvas width {width_inches:.2f} in ({width_inches * 2.54:.2f} cm) > 6.22 in (15.80 cm portrait text block)"
        )
    if width_inches > 12 or height_inches > 12:
        results["issues"].append(
            f"Unusually large: {width_inches:.1f} x {height_inches:.1f} inches"
        )
    if width_inches < 1 or height_inches < 1:
        results["issues"].append(
            f"Unusually small: {width_inches:.1f} x {height_inches:.1f} inches"
        )

    # 5. 空白区域检查（高数据墨水比的 lollipop/dumbbell/scatter 图背景天然以留白为主，仅拦截 >99% 近乎空白的异常渲染）
    img_array = np.array(img.convert("L"))
    white_ratio = (img_array > 250).sum() / img_array.size
    if white_ratio > 0.99:
        results["issues"].append(
            f"Blank or near-blank image: {white_ratio:.1%} of image is white"
        )

    # 6. 矢量格式与毕业论文排版审查
    pdf_path = png_path_obj.with_suffix(".pdf")
    svg_path = png_path_obj.with_suffix(".svg")
    if require_pdf and not pdf_path.exists():
        results["issues"].append("Missing PDF export")
    if not svg_path.exists():
        results["issues"].append("Missing SVG export")

    if mode == "thesis" and pdf_path.exists():
        pdf_issues, pdf_warnings = _audit_thesis_pdf_typography(pdf_path)
        results["issues"].extend(pdf_issues)
        results["warnings"].extend(pdf_warnings)

    if results["issues"]:
        results["passed"] = False

    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python qc.py <png_file_or_directory> [--mode thesis|publication|communication]")
        sys.exit(1)

    mode = "thesis"
    args = sys.argv[1:]
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 >= len(args):
            print("Error: --mode requires thesis, publication, or communication")
            sys.exit(1)
        mode = args[idx + 1].lower()
        args = args[:idx] + args[idx + 2 :]
        if mode not in {"thesis", "publication", "communication"}:
            print("Error: --mode must be thesis, publication, or communication")
            sys.exit(1)

    min_dpi = 600 if mode in {"thesis", "publication"} else 300
    require_pdf = mode in {"thesis", "publication"}

    target = Path(args[0])
    if target.is_dir():
        png_files = sorted(target.glob("*.png"))
        if not png_files:
            print(f"No PNG files found in {target}")
            sys.exit(1)
    else:
        png_files = [target]

    all_passed = True
    for png in png_files:
        qc = check_figure_quality(
            str(png),
            min_dpi=min_dpi,
            require_pdf=require_pdf,
            mode=mode,
        )
        icon = "PASS" if qc["passed"] else "FAIL"
        print(f"[{icon}] {png.name} (mode={mode})")
        for warn in qc.get("warnings", []):
            print(f"  [WARN] {warn}")
        if not qc["passed"]:
            all_passed = False
            for issue in qc["issues"]:
                print(f"  - {issue}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
