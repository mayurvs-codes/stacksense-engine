# StackSense: specification digest (source: official problem statement v1.0)

Individual online systems-design challenge, Synergy '26 (IIIT Bangalore). Build an **intelligent tech stack
recommendation engine**. Deadline **15 Nov 2026 23:59 IST**. Judges run it on 6 public + hidden scenarios.

## Functional requirements
FR1 input collection (UI or CLI, all mandatory fields; extras allowed and must be justified)
FR2 scenario import from JSON (standard schema; judges feed hidden scenarios this way)
FR3 recommend one choice for each of frontend, backend, database, hosting ("None" valid when justified)
FR4 supporting services when inputs call for them (cache, queue, search, auth, storage, cdn, realtime, payments, ml, ci_cd, observability)
FR5 per component: justification, driven_by input paths, >=1 alternative with why_not, trade-offs
FR6 monthly cost band in USD with assumptions
FR7 validation: field-level errors; detect contradictory/infeasible constraints, report as warnings with severity
FR8 JSON export per output schema
FR9 determinism: same input => same stack
NFR: runs locally from README in < 15 min (Win/macOS/Linux); no paid keys; recommendation < ~10 s; any language.

## Input schema (enum values are lower-case strings exactly as written)
| field | type | required | values / default |
|---|---|---|---|
| project.name | string | no | |
| project.type | enum | yes | content_site, web_app, saas_b2b, ecommerce, marketplace, social, realtime_collab, fintech, healthtech, data_analytics, iot, ai_ml_product, internal_tool, gaming, api_platform, other |
| project.description | string | no | free text (must NOT influence the stack in this engine) |
| project.platforms | list enum | yes, non-empty | web, android, ios, desktop, api_only |
| scale.users_at_launch | int >= 0 | yes | |
| scale.users_12_months | int >= 0 | yes | |
| scale.peak_concurrent_users | int >= 0 | no | |
| scale.traffic_pattern | enum | no | steady (default), spiky, seasonal |
| scale.workload | enum | no | read_heavy, balanced (default), write_heavy |
| scale.data_volume_gb_12_months | number >= 0 | no | |
| team.size | int >= 1 | yes | |
| team.experience | enum | yes | beginner, intermediate, senior, mixed |
| team.languages | list of lower-case strings | yes (may be empty) | python, typescript, java, csharp, php, go, kotlin, sql, ... |
| team.has_devops | bool | no | false |
| budget.monthly_infra_usd | number >= 0 | yes | |
| timeline.mvp_weeks | int >= 1 | yes | |
| infrastructure.cloud_preference | enum | no | any (default), aws, gcp, azure, none |
| infrastructure.deployment_model | enum | no | managed_cloud (default), self_hosted_cloud_vm, on_premise, air_gapped |
| infrastructure.data_residency | enum | no | none (default), india, eu, us, other |
| infrastructure.existing_systems | list of strings | no | [] |
| requirements.realtime / offline_support / full_text_search / file_media_storage / payments / multi_tenant / seo_critical | bool | no | false |
| requirements.auth | enum | no | none (default), email_password, social, phone_otp, enterprise_sso |
| requirements.ml_features | enum | no | none (default), inference_api, llm_rag, training |
| requirements.availability | string enum | no | "99", "99.9" (default), "99.95", "99.99" |
| requirements.p95_latency_ms | int > 0 or null | no | null |
| compliance | list enum | no | [] ; gdpr, dpdp, hipaa, pci_dss, rbi_localisation, soc2, iso27001 |
| priorities.<key> | int 1..5 | no | 3 ; keys cost, time_to_market, scalability, performance, maintainability, security |

Every default the engine applies MUST be listed in `assumptions[]`. Unknown extra keys must never crash the engine.
Scenario file = one JSON object `{"scenario_id": "...", "project": {...}, "scale": {...}, ...}` plus optional `"extra": {...}`.

### Extra parameters this engine must support (under `extra.`; ours, to score Input Design & Research)
`extra.expected_rps` (number), `extra.geo_distribution` (single_region|regional|global), `extra.vendor_lock_in_tolerance` (low|medium|high),
`extra.existing_licences` (list of strings), `extra.hiring_plan_6m` (int, engineers to hire), `extra.data_sensitivity` (public|internal|confidential|restricted),
`extra.integration_needs` (list: erp, crm, payments_gateway, sms, email, ...), `extra.sync_conflict_tolerance` (last_write_wins|merge|strict_consistency).
Each must change recommendations, warnings, cost or assumptions in a way you can explain and cite. Defaults go in `assumptions`.

## Output schema
Top level (required): `status` (ok | ok_with_warnings | infeasible | invalid_input), `summary`, `architecture_style`
(static, monolith, modular_monolith, serverless, service_oriented, microservices, hybrid, other), `stack`, `estimated_monthly_cost_usd`
`{min,max,assumptions[]}`, `warnings[]` `{code,severity(info|warning|critical),message,fields[]}`, `assumptions[]`, `validation_errors[]` `{field,message}`.
Also required by our gate: `engine_version`, `scenario_id` (echo only), `compliance_notes[]` (strings; non-empty when compliance or residency is set;
mention every compliance item and the residency by name; hipaa notes mention BAA), `integration_notes[]` (how each existing system is reused/integrated).
`stack.frontend|backend|database|hosting`: component objects. `stack.supporting[]`: component objects plus `layer`.
Component: `choice` (a real, currently maintained product that exists in the knowledge base, or "None" for core layers), `justification`
(scenario-specific, references actual input values), `driven_by[]` (input paths), `alternatives[]` `{choice, why_not}` (>=1 for core layers),
`tradeoffs[]`, and (core layers, required by our gate) `what_would_change[]`: counterfactuals, e.g. "If budget exceeded $X, choose Y".
invalid input => `status:"invalid_input"`, every problem in `validation_errors`, `stack:null`.
Constraints cannot all be met => `infeasible` with critical warnings, OR `ok_with_warnings` with a clearly reduced-scope stack whose `assumptions`
say exactly what was relaxed.

## Engine rules (violations are disqualifying or score-zero)
1. The stack decision must be made by YOUR logic (rules, weighted scoring, constraint solving). LLM output may NEVER pick or alter the stack.
   An LLM may only (a) parse description into suggested fields, (b) reword explanations. Must work fully with all LLM features off and produce
   the same stack. THIS ENGINE: implement no LLM calls in the decision path at all; any optional LLM helper lives only in `stacksense/llm_assist.py`.
2. Own knowledge base: strengths, limits, cost profile, ops burden, ecosystem, compliance/region support, maturity, lifecycle status, cited sources.
   Only real, currently maintained products. Deprecated/shut-down services are penalised. 6-8 options per core layer minimum.
3. Hard constraints (never violate silently): data_residency, compliance, deployment_model, explicit cloud_preference. Soft: budget, timeline, priorities.
4. Edge cases: missing fields; invalid values; contradictions (huge scale + zero budget, 99.99% + beginner solo, short timeline + many platforms);
   over-engineering traps (static/high-traffic, tiny internal tools => no microservices/Kubernetes without justification); regulatory;
   existing systems (reuse + say how); restricted deployment (on_premise/air_gapped => only self-hostable, no SaaS/CDN);
   skill mismatch (weigh team skills, explain trade-off); deprecated technology (never recommend; warn when found in existing_systems).

## Evaluation rubric
Recommendation Quality 35% (public + hidden scenarios; compared with judges' acceptable and known-bad stacks; hard constraints never violated;
consistency; small input changes => sensible local output changes). Input Design & Research 30% (inputs, validation, cited KB research).
Reasoning & Explainability 20% (driven_by, alternatives, honest trade-offs, plain-language warnings, scenario-specific text).
Documentation 15% (README that works, report with REAL screenshots from the running engine).
Hard-coded outputs for public scenarios, mocked screenshots, plagiarism => disqualification. Judges test modified versions of the public scenarios.

## CLI contract (gate depends on it)
`python -m stacksense run <scenario.json> --out <output.json>` : always writes the output JSON and exits 0 (even for invalid input);
exits non-zero only on engine bugs. `python -m stacksense serve --port N` : stdlib HTTP server; `GET /` returns the UI HTML;
`POST /api/recommend` (JSON body = scenario) returns the same JSON the CLI writes. Python >= 3.11, runtime dependencies: standard library only.
Knowledge base: `data/kb/*.json`, each file a JSON list of entries; fields: name, layer, lifecycle_status ("active"), languages[], regions[]
(e.g. "india","eu","us","global"), self_hostable (bool), saas_only (bool), cloud (aws|azure|gcp|neutral), cost_model, strengths, limits, ops_burden (1-5),
maturity, provides[] (supporting layers it natively covers, e.g. "auth","storage","realtime","search"), fts (bool, databases), sources[] `{url (https), title, accessed (YYYY-MM-DD)}`.
Layers: frontend, backend, database, hosting, cache, queue, search, auth, storage, cdn, realtime, payments, ml, ci_cd, observability, other.

## Submission (done by the owner, not the agent)
Drive folder `StackSense26_<FullName>/` containing `source/` (this repo minus junk, README.md, .env.example), `outputs/P1_output.json..P6_output.json`,
`Report_<FullName>.pdf` (<= 15 pages, template sections 1-11 incl. real screenshots and AI-assistance declaration).
