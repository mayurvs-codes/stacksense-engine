# PROGRESS

Built locally on 2026-11-13 (the cloud run never started). Branch `overnight/engine`. Gate notes are in `GATE_ISSUES.md`.

## Round 1: build
- Scaffolded `stacksense/` (validator, knowledge-base loader, decision engine, CLI, offline web UI) and the knowledge base
  (`tools/kb_source.py` writes `data/kb/*.json`; 129 entries (added managed Kubernetes on AWS/GCP/Azure, Cloud Spanner and .NET MAUI with opened sources; Kubernetes now needs high load or a big team)).
- Opened every KB source URL (`tools/verify_sources.py`), read the official region pages for AWS, Azure, Google Cloud, DigitalOcean, Vercel, Render,
  Supabase, Firestore and MongoDB Atlas, and checked open-source lifecycle through the GitHub API. This found that MinIO's repository is no longer
  maintained, so it was replaced by SeaweedFS. Details and limits of what was verified: `docs/KB_AUDIT.md`.
- Fixed while building: frameworks wrongly filtered by region rules; self-managed databases on serverless hosts; cost bands too high; list order
  made explanations non-deterministic; SQL Server reuse; compliance notes naming every regime.

## Rounds 2-10: adversarial review (`review/round_1` ... `review/round_10`)
- 32 + 25 + 25 hand-designed scenarios and 8 fuzz scans of 600 scenarios each (`tools/scan.py`), outputs read critically (critique file in each folder).
- Round 4 additionally fixed: a scoring bug that rewarded stacks for merely having more components (a 30M-user static site landed on Cloud Run),
  backends on static hosts, EOL databases (MongoDB) abandoned instead of upgraded, unattested SaaS under HIPAA/PCI, RBI + residency conflicts.
- Defects found and fixed at the root cause, each with a regression test: non-relational databases for relational workloads; a .NET-only auth
  library for non-.NET teams; content-site generators for interactive apps; end-of-life databases not flagged; CDN for Android-only apps;
  single ML slot for RAG apps; no trainable framework on-premises; static-site budget warning wording; $0-budget cost bands; licence matching;
  low lock-in tolerance; single-node capacity; load tier ignoring peak concurrency; SQLite on ephemeral hosts; Azure without a managed cache;
  HTMX at high scale or realtime.
- 135 unit and property tests (`python -m unittest discover -s tests -q`): all pass.
- `outputs/P1_output.json` ... `P6_output.json` generated from `outputs/inputs/`.

### Full gate output (verbatim tail of `python gate/run_gate.py`, no --quick)
```
PASS structure (0.0s)
PASS knowledge_base (0.0s)
PASS public_scenarios (0.3s)
PASS determinism_and_invariance (3.0s)
PASS llm_off_and_offline (3.2s)
PASS anti_hardcoding (0.0s)
PASS invalid_inputs (3.6s)
PASS minimal_input_defaults (0.2s)
PASS contradictions_and_hard_constraints (0.7s)
PASS extras_change_outputs (16.5s)
PASS fuzz_and_diversity (4.6s)
PASS local_sensitivity (5.4s)
PASS unit_tests (2.5s)
PASS web_ui (0.8s)
PASS docs (0.0s)
PASS gate_integrity (0.0s)

GATE: PASSED
```

## FINAL STATUS (honest)
- Gate: passes (output above). Unit tests: 135 pass.
- Exit condition (b): the last hand-written round (4) still found defects, which were fixed. After the last fix, 7 further fuzz scans (4,200 scenarios)
  found 0 oracle violations and only a borderline heuristic hit (about 1% Firestore-for-realtime/GCP choices, judged defensible). Round 6 found one small defect (fixed) and round 7 (15 more hand-written scenarios) found three (docs-site search, HTMX for realtime,
  low lock-in identity; all fixed). Round 8 (15 modified versions of the public scenarios, the kind the judges said they would run) found one (static host given a search server; fixed with Pagefind). Round 9 (robustness fuzz of 6,000 malformed inputs: 0 crashes; plus prose review: 4 wording/scale issues fixed). Round 10 (10 final scenarios on the newest KB entries) found one (HTMX at the highest load; fixed). Defects per hand-written round: 12+, 6, 5, 1, 3, 1, 1, so the "two consecutive clean rounds" condition is NOT met; diminishing
  but non-zero returns. Fuzz scans after the final fixes (3 more seeds) were clean for the oracle.
- Exit condition (c): every KB source page was opened and logged on 2026-11-13, but vendor compliance attestations, EU/US regions of several vendors and
  all ratings/costs are NOT verified claim by claim (see `docs/KB_AUDIT.md`, section "What was verified, honestly").
- Not done by design (owner's job): screenshots from the running engine, the PDF report, the Drive folder, the public GitHub link.
- Docker: the image was built and run on this machine (UI returned 200, API returned a recommendation); `docker compose up` itself was not run.
- Known limitations: no media pipeline in the KB, and some vendors (Neon, PlanetScale, Hetzner, Fly.io, CockroachDB) are absent; `on_premise` + payments is reported infeasible
  (gate rule conflict, see `GATE_ISSUES.md`); costs are order-of-magnitude estimates.
