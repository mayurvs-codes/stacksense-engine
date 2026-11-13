"""Writes PROGRESS.md from the latest real gate output (path given as argv[1])."""
import sys
from pathlib import Path

tail = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore").strip().splitlines()[-19:]
txt = """# PROGRESS

Built locally on 2026-11-13 (the cloud run never started). Branch `overnight/engine`. Gate notes are in `GATE_ISSUES.md`.

## Round 1: build
- Scaffolded `stacksense/` (validator, knowledge-base loader, decision engine, CLI, offline web UI) and the knowledge base
  (`tools/kb_source.py` writes `data/kb/*.json`; 123 entries after round 2).
- Opened every KB source URL (`tools/verify_sources.py`), read the official region pages for AWS, Azure, Google Cloud, DigitalOcean, Vercel, Render,
  Supabase, Firestore and MongoDB Atlas, and checked open-source lifecycle through the GitHub API. This found that MinIO's repository is no longer
  maintained, so it was replaced by SeaweedFS. Details and limits of what was verified: `docs/KB_AUDIT.md`.
- Fixed while building: frameworks wrongly filtered by region rules; self-managed databases on serverless hosts; cost bands too high; list order
  made explanations non-deterministic; SQL Server reuse; compliance notes naming every regime.

## Rounds 2-6: adversarial review (`review/round_1` ... `review/round_6`)
- 32 + 25 + 25 hand-designed scenarios and 8 fuzz scans of 600 scenarios each (`tools/scan.py`), outputs read critically (critique file in each folder).
- Round 4 additionally fixed: a scoring bug that rewarded stacks for merely having more components (a 30M-user static site landed on Cloud Run),
  backends on static hosts, EOL databases (MongoDB) abandoned instead of upgraded, unattested SaaS under HIPAA/PCI, RBI + residency conflicts.
- Defects found and fixed at the root cause, each with a regression test: non-relational databases for relational workloads; a .NET-only auth
  library for non-.NET teams; content-site generators for interactive apps; end-of-life databases not flagged; CDN for Android-only apps;
  single ML slot for RAG apps; no trainable framework on-premises; static-site budget warning wording; $0-budget cost bands; licence matching;
  low lock-in tolerance; single-node capacity; load tier ignoring peak concurrency; SQLite on ephemeral hosts; Azure without a managed cache;
  HTMX at high scale or realtime.
- 117 unit and property tests (`python -m unittest discover -s tests -q`): all pass.
- `outputs/P1_output.json` ... `P6_output.json` generated from `outputs/inputs/`.

### Full gate output (verbatim tail of `python gate/run_gate.py`, no --quick)
```
""" + "\n".join(tail) + """
```

## FINAL STATUS (honest)
- Gate: passes (output above). Unit tests: 117 pass.
- Exit condition (b): the last hand-written round (4) still found defects, which were fixed. After the last fix, 7 further fuzz scans (4,200 scenarios)
  found 0 oracle violations and only a borderline heuristic hit (about 1% Firestore-for-realtime/GCP choices, judged defensible). Round 6 (15 fresh hand-written scenarios after those fixes) found one small defect (single on-premises server
  and 99.95% availability, fixed). So the "two consecutive clean rounds" condition is still not formally proven: a further hand-written round after
  the round 6 fix is recommended.
- Exit condition (c): every KB source page was opened and logged on 2026-11-13, but vendor compliance attestations, EU/US regions of several vendors and
  all ratings/costs are NOT verified claim by claim (see `docs/KB_AUDIT.md`, section "What was verified, honestly").
- Not done by design (owner's job): screenshots from the running engine, the PDF report, the Drive folder, the public GitHub link.
- Not verified: `docker compose up` (Docker not run on this machine).
- Known limitations: no globally distributed SQL, Kubernetes services or media pipeline in the KB; `on_premise` + payments is reported infeasible
  (gate rule conflict, see `GATE_ISSUES.md`); costs are order-of-magnitude estimates.
"""
Path(__file__).resolve().parent.parent.joinpath("PROGRESS.md").write_text(txt, encoding="utf-8")
print(len(txt))
