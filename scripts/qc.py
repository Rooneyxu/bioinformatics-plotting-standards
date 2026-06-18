#!/usr/bin/env python3
"""
图表质量检查脚本。
保存图表后运行，验证 DPI、尺寸、空白率、矢量格式是否齐全。

用法：
    python scripts/qc.py figure_name.png
    python scripts/qc.py figure_name.png --mode publication
    python scripts/qc.py figure_name.png --mode communication
    python scripts/qc.py output/ --mode publication
"""
import sys
from pathlib import Path

def check_figure_quality(
    png_path: str,
    min_dpi: int = 600,
    require_pdf: bool = True,
) -> dict:
    """
    检查保存的图表质量。
    返回检查结果字典，包含通过/失败状态和详细信息。

    检查项：
    1. 文件存在且非空
    2. DPI >= min_dpi（出版要求 600）
    3. 尺寸合理（1-12 inches）
    4. 空白区域 < 85%
    5. PDF 和 SVG 矢量格式同步导出
    """
    from PIL import Image
    import numpy as np

    png_path = Path(png_path)
    results = {"path": str(png_path), "passed": True, "issues": []}

    # 1. 文件存在性检查
    if not png_path.exists():
        results["passed"] = False
        results["issues"].append(f"File not found: {png_path}")
        return results

    # 2. 文件大小检查（过小可能是空白图）
    file_size_kb = png_path.stat().st_size / 1024
    if file_size_kb < 10:
        results["passed"] = False
        results["issues"].append(f"File too small ({file_size_kb:.1f} KB) — likely blank")

    # 3. 分辨率检查
    img = Image.open(png_path)
    width_px, height_px = img.size
    dpi_info = img.info.get('dpi', (72, 72))
    actual_dpi = dpi_info[0] if isinstance(dpi_info, tuple) else dpi_info

    if actual_dpi < min_dpi:
        results["issues"].append(
            f"DPI too low: {actual_dpi} (expected >= {min_dpi})")

    # 4. 尺寸合理性检查（出版要求宽度 89-180mm）
    width_inches = width_px / actual_dpi if actual_dpi > 0 else 0
    height_inches = height_px / actual_dpi if actual_dpi > 0 else 0
    if width_inches > 12 or height_inches > 12:
        results["issues"].append(
            f"Unusually large: {width_inches:.1f} x {height_inches:.1f} inches")
    if width_inches < 1 or height_inches < 1:
        results["issues"].append(
            f"Unusually small: {width_inches:.1f} x {height_inches:.1f} inches")

    # 5. 空白区域检查（检测是否有大面积空白）
    img_array = np.array(img.convert('L'))  # 转灰度
    white_ratio = (img_array > 250).sum() / img_array.size
    if white_ratio > 0.85:
        results["issues"].append(
            f"Excessive whitespace: {white_ratio:.0%} of image is white")

    # 6. 同时检查矢量格式是否存在
    pdf_path = png_path.with_suffix('.pdf')
    svg_path = png_path.with_suffix('.svg')
    if require_pdf and not pdf_path.exists():
        results["issues"].append("Missing PDF export")
    if not svg_path.exists():
        results["issues"].append("Missing SVG export")

    if results["issues"]:
        results["passed"] = False

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python qc.py <png_file_or_directory> [--mode publication|communication]")
        sys.exit(1)

    mode = "publication"
    args = sys.argv[1:]
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 >= len(args):
            print("Error: --mode requires publication or communication")
            sys.exit(1)
        mode = args[idx + 1].lower()
        args = args[:idx] + args[idx + 2 :]
        if mode not in {"publication", "communication"}:
            print("Error: --mode must be publication or communication")
            sys.exit(1)

    min_dpi = 600 if mode == "publication" else 300
    require_pdf = mode == "publication"

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
        )
        icon = "PASS" if qc["passed"] else "FAIL"
        print(f"[{icon}] {png.name}")
        if not qc["passed"]:
            all_passed = False
            for issue in qc["issues"]:
                print(f"  - {issue}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
