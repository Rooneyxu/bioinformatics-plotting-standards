#!/usr/bin/env python3
"""
Grade publication/communication export assertions for bio plot eval runs.

Usage (from skill root):
  python evals/grade_outputs.py <outputs_dir> --mode publication
  python evals/grade_outputs.py <outputs_dir> --mode communication
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
QC_SCRIPT = SKILL_ROOT / "scripts" / "qc.py"


def find_pngs(outputs_dir: Path) -> list[Path]:
    return sorted(outputs_dir.rglob("*.png"))


def grade(outputs_dir: Path, mode: str) -> dict:
    outputs_dir = Path(outputs_dir)
    pngs = find_pngs(outputs_dir)
    expectations: list[dict] = []

    if not pngs:
        expectations.append({
            "text": "At least one PNG figure exists in outputs",
            "passed": False,
            "evidence": f"No PNG found under {outputs_dir}",
        })
    else:
        expectations.append({
            "text": "At least one PNG figure exists in outputs",
            "passed": True,
            "evidence": f"Found: {[p.name for p in pngs]}",
        })

    if pngs and QC_SCRIPT.exists():
        png = pngs[0]
        proc = subprocess.run(
            [sys.executable, str(QC_SCRIPT), str(png), "--mode", mode],
            capture_output=True,
            text=True,
        )
        passed = proc.returncode == 0
        expectations.append({
            "text": f"qc.py --mode {mode} passes on primary PNG",
            "passed": passed,
            "evidence": (proc.stdout + proc.stderr).strip() or "qc.py produced no output",
        })

        pdf = png.with_suffix(".pdf")
        svg = png.with_suffix(".svg")
        if mode == "publication":
            expectations.append({
                "text": "Publication bundle includes PDF and SVG beside PNG",
                "passed": pdf.exists() and svg.exists(),
                "evidence": f"pdf={pdf.exists()}, svg={svg.exists()}",
            })
        else:
            expectations.append({
                "text": "Communication bundle includes SVG beside PNG",
                "passed": svg.exists(),
                "evidence": f"svg={svg.exists()}, pdf_optional={pdf.exists()}",
            })

    passed_n = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed_n,
            "failed": total - passed_n,
            "total": total,
            "pass_rate": round(passed_n / total, 2) if total else 0.0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs_dir")
    parser.add_argument("--mode", choices=["publication", "communication"], default="publication")
    parser.add_argument("--out", default=None, help="Write grading.json path")
    args = parser.parse_args()

    result = grade(Path(args.outputs_dir), args.mode)
    out_path = Path(args.out) if args.out else Path(args.outputs_dir) / "grading.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
