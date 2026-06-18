#!/usr/bin/env python3
"""Grade bio plot skill eval runs. Usage:
  python evals/grade_all_evals.py <workspace>/iteration-N
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".png", ".svg", ".pdf", ".tiff", ".jpg", ".jpeg"}


def strip_comments(code: str) -> str:
    code = re.sub(r"#.*", "", code)
    code = re.sub(r"//.*", "", code)
    return code


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has_figure_files(outputs: Path) -> bool:
    return any(p.suffix.lower() in IMAGE_EXTS for p in outputs.rglob("*") if p.is_file())


def code_files_text(outputs: Path, strip: bool = True) -> str:
    text = ""
    for p in outputs.rglob("*"):
        if p.suffix.lower() in {".py", ".r", ".R"} and p.is_file():
            chunk = p.read_text(encoding="utf-8", errors="replace")
            text += strip_comments(chunk) if strip else chunk
            text += "\n"
    return text


def grade_assertion(name: str, desc: str, outputs: Path, cfg: str, eval_id: str) -> dict:
    transcript = read_text(outputs / "transcript.md")
    response = read_text(outputs / "response.md")
    combined = transcript + "\n" + response
    code_text = code_files_text(outputs, strip=True)

    passed, evidence = False, ""

    if name == "no_figure_created":
        passed = not has_figure_files(outputs)
        evidence = f"figure_files={has_figure_files(outputs)}"

    elif name == "table_delivered":
        csvs = list(outputs.glob("*.csv"))
        passed = bool(csvs) or "top20" in combined.lower()
        evidence = f"csv={[c.name for c in csvs]}"

    elif name == "no_data_plot_backend":
        passed = not re.search(r"^\s*(import|from)\s+(matplotlib|seaborn|ggplot2)|savefig|ggsave|geom_", code_text, re.I | re.M)
        evidence = "executable code only, comments stripped"

    elif name == "generate_image_routed":
        passed = bool(re.search(r"GenerateImage|generate.?image", combined, re.I))
        evidence = "GenerateImage in transcript/response"

    elif name == "redirects_to_nature_figure":
        redirected = bool(re.search(r"nature-figure", combined, re.I))
        built = any("multipanel" in p.name.lower() or "fig1" in p.name.lower() for p in outputs.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
        passed = redirected and not built
        evidence = f"redirect={redirected}, built={built}"

    elif name == "does_not_assemble_full_figure":
        built = any("multipanel" in p.name.lower() or "fig1" in p.name.lower() for p in outputs.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
        passed = not built
        evidence = f"multipanel_output={built}"

    elif name == "assembles_simple_multipanel":
        passed = has_figure_files(outputs) and bool(re.search(r"subplot|GridSpec|mosaic|patchwork|1x2|2.?panel", code_text + combined, re.I))
        evidence = f"has_figure={has_figure_files(outputs)}"

    elif name == "does_not_redirect_nature_figure":
        passed = not re.search(r"转用 nature-figure|use nature-figure skill", combined, re.I) or re.search(r"本 skill|patchwork|subplot", combined, re.I)
        evidence = "no full redirect to nature-figure for simple panel"

    elif name == "communication_export":
        pngs, svgs, pdfs = list(outputs.glob("*.png")), list(outputs.glob("*.svg")), list(outputs.glob("*.pdf"))
        passed = bool(pngs and svgs) and len(pdfs) == 0
        evidence = f"png={len(pngs)}, svg={len(svgs)}, pdf={len(pdfs)}"

    elif name == "defaults_python_without_asking":
        asked = bool(re.search(r"Python.*(还是|or).*R|Python 还是 R", combined, re.I))
        uses_py = bool(re.search(r"matplotlib|seaborn|\.py", code_text + combined, re.I))
        passed = uses_py and not asked
        evidence = f"asked={asked}, python={uses_py}"

    elif name == "figure_or_script_produced":
        passed = has_figure_files(outputs) or bool(list(outputs.glob("*.py")))
        evidence = "figure or script present"

    elif name == "asks_backend_before_plotting":
        passed = bool(re.search(r"Python.*(还是|or).*R|Python 还是 R", combined, re.I))
        evidence = "backend question in response"

    elif name == "does_not_default_python":
        passed = not has_figure_files(outputs)
        evidence = f"no figure before answer: {not has_figure_files(outputs)}"

    elif name == "no_cross_backend_rendering":
        if "python" in eval_id:
            passed = not re.search(r"^\s*(library\(ggplot2\)|geom_|ggplot2::)", code_text, re.I | re.M)
        else:
            passed = not re.search(r"^\s*(import matplotlib|import seaborn|from matplotlib|savefig)", code_text, re.I | re.M)
        passed = passed and not has_figure_files(outputs) if "missing" in eval_id or "blocker" in eval_id else passed
        if "missing" in eval_id or "blocker" in eval_id:
            passed = passed and not any(p.suffix.lower() in IMAGE_EXTS for p in outputs.rglob("*") if p.is_file() and "mock" not in p.name)
        evidence = "cross-backend check on stripped code"

    elif name == "blocker_reported":
        passed = bool(re.search(r"未安装|不可用|missing|not installed|blocker|ModuleNotFound|command not found", combined, re.I))
        evidence = "blocker language found"

    elif name == "publication_export_bundle":
        pngs = list(outputs.glob("*.png"))
        if pngs:
            base = pngs[0].with_suffix("")
            passed = base.with_suffix(".pdf").exists() and base.with_suffix(".svg").exists()
            evidence = f"pdf={base.with_suffix('.pdf').exists()}, svg={base.with_suffix('.svg').exists()}"
        else:
            passed = False
            evidence = "no png"

    elif name == "uses_adjusttext_or_equivalent":
        passed = bool(re.search(r"adjustText|adjust_text", code_text, re.I))
        evidence = "adjustText in code"

    elif name == "publication_qc_mentioned_or_run":
        passed = bool(re.search(r"qc\.py.*publication|--mode publication", combined, re.I))
        evidence = "qc publication mentioned"

    elif name == "italic_gene_labels":
        passed = bool(re.search(r"italic|fontstyle=.italic|fontface=.italic", code_text, re.I))
        evidence = "italic in code"

    elif name == "communication_export_only":
        passed = bool(list(outputs.glob("*.png")) and list(outputs.glob("*.svg")))
        evidence = "svg+png present"

    elif name == "not_publication_triple_bundle":
        pdfs = list(outputs.glob("*.pdf"))
        passed = len(pdfs) == 0 or "communication" in combined.lower()
        evidence = f"pdf_count={len(pdfs)}"

    elif name == "qc_communication_mode":
        passed = bool(re.search(r"communication|qc\.py", combined, re.I)) or has_figure_files(outputs)
        evidence = "communication qc or figure ok"

    elif name == "no_jet_rainbow":
        passed = not re.search(r"cmap\s*=\s*['\"]jet['\"]|cmap\s*=\s*['\"]rainbow['\"]", code_text, re.I)
        evidence = "no jet/rainbow cmap"

    elif name == "nmi_pastel_or_documented":
        passed = bool(re.search(r"NMI_PASTEL|DEFAULT_COLORS_NMI|#484878|nmi.?pastel", code_text + combined, re.I))
        evidence = "NMI pastel referenced"

    elif name == "r_only_stack":
        passed = bool(re.search(r"ggplot2|ggprism|ggrepel", code_text, re.I)) and not re.search(r"import matplotlib|savefig", code_text, re.I)
        evidence = "R stack in code"

    elif name == "ggrepel_used":
        passed = bool(re.search(r"ggrepel|geom_text_repel", code_text, re.I))
        evidence = "ggrepel in code"

    else:
        evidence = f"unknown assertion {name}"

    return {"text": f"{name}: {desc}", "passed": passed, "evidence": evidence}


def grade_run(ws: Path, eval_id: str, cfg: str) -> dict:
    run_dir = ws / eval_id / cfg
    outputs = run_dir / "outputs"
    meta = json.loads((run_dir / "eval_metadata.json").read_text(encoding="utf-8"))
    expectations = [grade_assertion(a["name"], a["description"], outputs, cfg, eval_id) for a in meta.get("assertions", [])]

    if eval_id == "publication-volcano-python" and cfg == "with_skill":
        pngs = list(outputs.glob("*.png"))
        if pngs:
            proc = subprocess.run([sys.executable, str(SKILL_ROOT / "scripts/qc.py"), str(pngs[0]), "--mode", "publication"], capture_output=True, text=True)
            expectations.append({"text": "qc.py publication", "passed": proc.returncode == 0, "evidence": (proc.stdout + proc.stderr)[:300]})

    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    result = {"eval_id": eval_id, "configuration": cfg, "expectations": expectations, "summary": {"passed": passed, "failed": total - passed, "total": total, "pass_rate": round(passed / total, 3) if total else 0}}
    (run_dir / "grading.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main():
    ws = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/rooneyxu/projects/bioinformatics-plotting-standards-workspace/iteration-2")
    evals = json.loads((SKILL_ROOT / "evals/evals.json").read_text())["evals"]
    for ev in evals:
        for cfg in ("with_skill", "without_skill"):
            if not (ws / ev["id"] / cfg / "outputs").exists():
                continue
            r = grade_run(ws, ev["id"], cfg)
            s = r["summary"]
            print(f"[{'PASS' if s['failed']==0 else 'FAIL'}] {ev['id']} / {cfg}: {s['passed']}/{s['total']}")


if __name__ == "__main__":
    main()
