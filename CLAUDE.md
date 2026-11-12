# OVERNIGHT BUILD PROTOCOL: read fully before doing anything

You are building the StackSense recommendation engine for a hackathon where the owner wants a **top-3 finish**.
Read `docs/SPEC.md` (requirements), `data/scenarios/public_scenarios.json`, and `gate/` (the validation gate).
Work on branch `overnight/engine` (create from `main`), commit and push after every round. Never push to `main`.

## Non-negotiable rules (breaking any = the run is worthless)
1. **Never edit** `gate/`, `data/scenarios/`, `docs/SPEC.md` or this file. If you believe the gate is wrong, append the reason to
   `GATE_ISSUES.md` and keep working; the owner decides. Weakening the gate in any way is cheating.
2. **No hard-coding or cheating.** No logic keyed on scenario ids, project names, descriptions, or the public scenarios' values; no canned outputs;
   no reading `outputs/` or scenario files at runtime. Decisions come from general rules + weighted scoring over the knowledge base.
   The stack must NOT depend on `project.description`. Hidden scenarios and modified public scenarios will be used by the judges.
3. **No LLM in the decision path, ever.** Standard library only at runtime (Python >= 3.11). No network access at runtime.
4. **Facts must be real.** Every KB entry needs real, current (2026) facts and `https` sources you actually opened with WebFetch/WebSearch
   (accessed date = the day you checked). Never invent products, prices, regions or compliance claims; if you cannot verify, say so in
   `docs/KB_AUDIT.md` and keep the entry conservative (e.g. omit the region/compliance claim). Only `lifecycle_status: "active"` products.
5. **Be honest.** `PROGRESS.md` must contain, each round, the verbatim tail of the real gate output and what you changed. Never claim a gate pass
   you did not run. If you are stuck, say so; do not paper over it.
6. Do not generate screenshots or the PDF report (the owner does that). You DO write `README.md` and `docs/REPORT_NOTES.md` (material for the report:
   architecture, input-design rationale per field, decision logic, KB methodology, edge-case table, validation approach, limitations; >= 6000 chars).

## The loop (repeat until the exit condition holds)
**ROUND N**
1. `python gate/run_gate.py --json > gate_report.json` (use `--quick` while iterating; the final round of each pass must be the full run).
2. If anything FAILS: find the ROOT CAUSE in engine logic or KB (never special-case the failing input), fix, add/extend unit tests in `tests/`,
   commit + push, go to step 1.
3. When the gate is fully green, run the **adversarial phase**: write 25 NEW scenarios in `review/round_N/` that you have not used before,
   covering these classes at least twice each: invalid inputs, contradictions, over-engineering traps, regulated (hipaa/pci/rbi/gdpr/dpdp) systems,
   existing/legacy systems (incl. EOL ones), on_premise/air_gapped, skill mismatch, offline-first, realtime at scale, ML/LLM apps, extreme budgets,
   minimal-field files, extras-heavy files. Run the engine, and for EACH output write a skeptical critique in `review/round_N/critique.md` as a
   senior architect and as a judge using the rubric: would a defensible expert reject any choice? any hard-constraint violation? generic text?
   wrong cost order of magnitude? missing integration/compliance note? Every defect found => fix the root cause + add a regression test.
4. **Research phase** (each round): re-verify at least 10 KB entries against their official sources (WebFetch/WebSearch), fix wrong or stale facts,
   update `accessed` dates, add missing mainstream options and supporting services, record each check in `docs/KB_AUDIT.md`
   (entry, source, what was verified, date). Over the run, every entry must be audited at least once and the KB should cover widely used
   options (e.g. multiple front-end frameworks/meta-frameworks, backend frameworks per major language, SQL/NoSQL/search/time-series DBs, PaaS/serverless/
   container/VM/on-prem hosts across AWS/Azure/GCP/neutral providers, and India/EU/US region availability where claimed).
5. Update `PROGRESS.md`, commit, push. Start ROUND N+1.

## Quality bar: what "top-3 worthy" means here (judge as the harshest reviewer would)
- All four rubric areas strong: hard constraints never violated; recommendations an experienced engineer would accept; explanations tied to
  actual input values with real alternatives, trade-offs, and `what_would_change` counterfactuals; cost bands in the right order of magnitude.
- A single recommendation must run well under 5 s; output deterministic byte-for-byte.
- UI: `python -m stacksense serve` gives a clean, usable single-page UI (form with all mandatory + extra fields, scenario JSON import,
  result view with justification/alternatives/warnings/cost, JSON download). Plain HTML/CSS/JS served by the stdlib server, no CDN assets
  (must work offline).
- README meets the problem statement 9.4 list (name+overview, architecture diagram (ASCII is fine) + module descriptions + data flow, tech with versions,
  prerequisites, setup/run steps, how to run a scenario JSON and where output goes, how to switch LLM off (state that no LLM is used), project
  structure, credits for every third-party source/dataset/API).
- >= 60 meaningful unit tests (also property-style: determinism, order-invariance, hard-constraint invariants) and clean `python -m unittest`.

## EXIT CONDITION (all must be true, otherwise keep looping)
(a) the full gate (`python gate/run_gate.py`, no `--quick`) exits 0 in the final round;
(b) the last TWO consecutive adversarial rounds found zero new defects;
(c) every KB entry appears in `docs/KB_AUDIT.md` as verified against a source this run, and none is flagged unverifiable without being made conservative;
(d) README, `docs/REPORT_NOTES.md`, UI and tests satisfy the quality bar above;
(e) `PROGRESS.md` ends with a section `FINAL STATUS` listing the last gate output verbatim, known limitations, and anything unverified.
Hard stops: after 14 rounds or if you run out of budget, stop and write an honest FINAL STATUS describing what is NOT done. Do not pretend.
Order of work for round 1: scaffold `stacksense/` package + CLI contract, validator + defaults, KB schema with ~10 verified entries per core layer,
decision pipeline (derive features -> architecture style -> hard filter -> weighted score -> supporting rules -> conflicts/warnings -> cost -> explanation),
then iterate with the gate.
