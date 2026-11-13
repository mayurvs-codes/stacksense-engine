# StackSense: deterministic tech stack recommendation engine

StackSense takes structured project parameters (scale, team, budget, infrastructure and compliance constraints, requirements, priorities)
and recommends a frontend, backend, database and hosting stack plus supporting services, each with a scenario-specific justification, the
input fields that drove it, alternatives with the reason they lost, trade-offs, "what would change this choice" counterfactuals and an
estimated monthly cost band. Hard constraints (data residency, compliance, deployment model, explicit cloud preference) are never violated
silently; contradictions are reported as warnings with a severity. The decision logic is rules plus weighted scoring over a curated, cited
knowledge base. **No LLM is used anywhere**, the same input always gives the same output, and the engine needs no network access or API keys.

Built for the StackSense Challenge at Synergy '26 (IIIT Bangalore). Author: see the report title page.

## Prerequisites

- Python 3.11 or newer (developed and tested on Python 3.13). Windows, macOS and Linux are supported.
- No third-party packages, no database, no API keys. Docker is optional.

## Setup and run (about two minutes)

```bash
git clone <this repository>
cd <repository folder>
python -m stacksense run scenario.json --out result.json
```

That is the whole setup: there is nothing to install.

### Run a scenario file

A scenario is a JSON object in the standard input schema (see `docs/SPEC.md`; the six public scenarios are in `data/scenarios/`).
Run one scenario file and write the result JSON next to it:

```bash
python -m stacksense run path/to/scenario.json --out path/to/result.json
```

- The result JSON follows the output schema (`status`, `summary`, `architecture_style`, `stack`, `estimated_monthly_cost_usd`,
  `warnings`, `assumptions`, `validation_errors`, plus `compliance_notes` and `integration_notes`).
- Without `--out` the JSON is printed to standard output.
- The command exits with code 0 even for invalid input (the result then has `"status": "invalid_input"` and field-level errors);
  it exits non-zero only on an engine bug or an unreadable file.

### Web UI

```bash
python -m stacksense serve --port 8000
```

Open http://127.0.0.1:8000. The UI is a single static page served by the Python standard library and works offline: fill the form
(or load a scenario JSON file), press **Recommend a stack**, inspect every component's justification, alternatives and counterfactuals,
and download the result JSON. The same engine answers `POST /api/recommend` with a scenario JSON body.

### Docker (optional)

```bash
docker compose up --build   # UI on http://localhost:8000
```

### Tests and validation

```bash
python -m unittest discover -s tests -q      # unit and property tests
python gate/run_gate.py --quick              # strict validation gate (hard constraints, determinism, edge cases, fuzzing)
```

## LLM switch

There is nothing to switch off: the engine contains no LLM call, no model download and no network code in the decision path
(`STACKSENSE_LLM=off` is the default in `.env.example` and is accepted but unused). The stack is chosen only by rules and scoring
in `stacksense/engine.py` over the data in `data/kb/`. `project.description` is deliberately ignored, so free text can never change the stack.

## Architecture

```
 scenario.json ──► validate.py ──► derive features ──► hard-constraint filters ──► joint scoring ──► explanations ──► result.json
 (CLI / UI / API)  field errors,    scale tier, ops     cloud pref, deployment,    for every viable     driven_by,        status, stack,
                   defaults →       capacity, weights   residency, compliance,     hosting option:      alternatives,     cost band,
                   assumptions      from priorities     realtime, runtime fit      best backend,        trade-offs,       warnings,
                                                                                    frontend, database,  counterfactuals   assumptions
                                    data/kb/*.json  ─────────────────────────────►  supporting services
```

| Module | Responsibility |
|---|---|
| `stacksense/validate.py` | Type/range/enum validation of every field, reports all errors at once, applies documented defaults and records each one in `assumptions`, canonicalises list order. |
| `stacksense/kb.py` | Loads the knowledge base, verified region notes and the end-of-life lifecycle rules. |
| `stacksense/engine.py` | Feature derivation, hard-constraint filters, scoring, joint selection, warnings, cost model, explanations and output assembly. |
| `stacksense/cli.py`, `server.py`, `static/index.html` | Command line, local HTTP server and offline web UI. |
| `data/kb/*.json` | 123 curated technologies (frontend, backend, database, hosting and 11 supporting layers) with strengths, limits, regions, ratings, cost estimates and source URLs. |
| `tools/` | Knowledge-base generator and audit scripts (`kb_source.py`, `verify_sources.py`, `gen_kb_audit.py`). |
| `gate/` | Independent validation gate used during development. |

Data flow: the validator turns raw JSON into a normalised scenario (plus assumptions). The engine derives features (scale tier from users and
requests per second, operations capacity from experience, DevOps and team size, scoring weights from the priorities). For each hosting
option that passes the hard constraints it builds the best backend, frontend, database and supporting services for that host (so cloud
affinity, runtime fit, websocket support and self-hosting rules are honoured together), scores the whole stack, and keeps the best.
Warnings, the cost band, compliance and integration notes and the explanations are produced from the chosen stack.

## Technology used to build the engine

Python 3.11+ (standard library only: `json`, `re`, `http.server`, `argparse`, `unittest`), HTML/CSS/vanilla JavaScript for the UI.
No frameworks, no build step, no third-party packages. Engine version 1.0.0.

## Project structure

```
stacksense/            engine package (validate.py, kb.py, engine.py, cli.py, server.py, static/index.html)
data/kb/               knowledge base (frontend, backend, database, hosting, supporting)
data/region_notes.json verified region names per vendor
data/scenarios/        the six public scenarios (input only)
docs/                  SPEC.md (requirements digest), KB_AUDIT.md (what was verified), REPORT_NOTES.md (report material)
tests/                 unit and property tests
tools/                 knowledge-base generator, source verification, audit generator
gate/                  strict validation gate (independent of the engine)
review/                adversarial review rounds
```

## Credits

- Knowledge-base facts come from the official documentation and pricing pages linked per entry in `data/kb/*.json` and listed in
  `docs/KB_AUDIT.md` (AWS, Microsoft Azure, Google Cloud, DigitalOcean, Vercel, Render, Supabase, Firebase, MongoDB, Cloudflare, Netlify,
  GitHub, Razorpay, Stripe and the open-source project sites).
- Region availability was read from the official region pages of AWS, Azure, Google Cloud, DigitalOcean, Vercel, Render, Supabase,
  Firestore and MongoDB Atlas on 2026-11-13.
- Open-source project lifecycle was checked with the public GitHub API.
- No third-party library, dataset or API is used at runtime. Built with the assistance of Claude Code (declared in the report).
