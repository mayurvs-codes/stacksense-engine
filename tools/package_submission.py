"""Assembles the Drive folder layout required by the problem statement:

StackSense26_<FullName>/
  source/   (repository without caches, junk, screenshots, previous submission builds)
  outputs/  (P1_output.json ... P6_output.json)
  Report_<FullName>.pdf
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
full = sys.argv[1] if len(sys.argv) > 1 else "Mayurvs"
dest = ROOT / "submission" / f"StackSense26_{full}"
if dest.exists():
    shutil.rmtree(dest)
(dest / "source").mkdir(parents=True)
(dest / "outputs").mkdir()
SKIP_DIRS = {".git", "__pycache__", "submission", "extracted", "heldout", "report", "outputs", ".venv", "node_modules", ".claude"}
SKIP_FILES = {"gate_report.json"}


def ignore(directory, names):
    out = set()
    for n in names:
        p = Path(directory) / n
        if n in SKIP_DIRS and Path(directory) == ROOT:
            out.add(n)
        elif n == "__pycache__" or n.endswith((".pyc", ".zip")) or n in SKIP_FILES:
            out.add(n)
    return out


shutil.copytree(ROOT, dest / "source", ignore=ignore, dirs_exist_ok=True)
for i in range(1, 7):
    shutil.copy2(ROOT / "outputs" / f"P{i}_output.json", dest / "outputs" / f"P{i}_output.json")
shutil.copy2(ROOT / "report" / "report.pdf", dest / f"Report_{full}.pdf")
size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
print(dest, f"{size / 1e6:.1f} MB", len(list(dest.rglob('*'))), "entries")
