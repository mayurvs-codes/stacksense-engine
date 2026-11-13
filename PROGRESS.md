# PROGRESS

Built locally (the cloud run never started). Branch: `overnight/engine`. Gate notes are in `GATE_ISSUES.md`.

## Round 1 (2026-11-13)
- Scaffolded `stacksense/` (validator, knowledge-base loader, decision engine, CLI, offline web UI) and 121 knowledge-base entries
  (`tools/kb_source.py` writes `data/kb/*.json`).
- Opened every KB source URL (`tools/verify_sources.py`: 122 of 123 by script, 1 in the browser pane), read the official region pages for AWS, Azure,
  Google Cloud, DigitalOcean, Vercel, Render, Supabase, Firestore and MongoDB Atlas, and checked open-source lifecycle through the GitHub API.
  This found that MinIO's repository is no longer maintained, so it was replaced with SeaweedFS. Details are in `docs/KB_AUDIT.md`.
- Fixed during the round: frameworks were wrongly filtered by region/deployment rules; self-managed databases landed on serverless hosts; cost bands
  were too high (rescaled, added a correlation factor); optional components are deferred when the estimate is far above the budget; list order
  is canonicalised so the text is deterministic; reuse of existing supported databases (SQL Server) is honoured; compliance notes name every regime.
- Wrote 87 unit and property tests, README, `docs/REPORT_NOTES.md`, Dockerfile and compose file (the Docker build was NOT run on this machine).
- Known gate note: `on_premise` + payments cannot satisfy the gate's SaaS rule, so the engine reports `infeasible` (see `GATE_ISSUES.md`).

### Full gate output (verbatim tail of `python gate/run_gate.py`, no --quick)
```
PASS structure (0.0s)
PASS knowledge_base (0.0s)
PASS public_scenarios (0.2s)
PASS determinism_and_invariance (2.6s)
PASS llm_off_and_offline (2.7s)
PASS anti_hardcoding (0.0s)
PASS invalid_inputs (2.9s)
PASS minimal_input_defaults (0.1s)
PASS contradictions_and_hard_constraints (0.5s)
PASS extras_change_outputs (14.1s)
PASS fuzz_and_diversity (3.7s)
PASS local_sensitivity (4.4s)
PASS unit_tests (1.3s)
PASS web_ui (0.7s)
PASS docs (0.0s)
PASS gate_integrity (0.0s)

GATE: PASSED
```
Unit tests: `python -m unittest discover -s tests -q` -> Ran 87 tests, OK.

## Next
Adversarial review rounds in `review/round_N/`, KB re-verification, UI and README polish. Screenshots and the PDF report are done by the owner.
