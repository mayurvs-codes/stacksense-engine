# Report notes (material for the PDF report)

These notes follow the template in the problem statement (sections 1-11). They describe what the engine actually does; numbers
come from the repository. Screenshots must be taken by the owner from the running engine.

## 1. Abstract (draft, under 150 words)
StackSense is a deterministic tech-stack recommendation engine. It validates a scenario, derives features (scale tier, operations capacity,
priority weights), filters a curated 123-entry knowledge base with hard constraints (data residency, compliance, deployment model, explicit
cloud preference), jointly scores hosting, backend, frontend, database and supporting services, and explains every choice with the input fields
that drove it, alternatives, trade-offs and counterfactuals. Contradictions become severity-labelled warnings, the budget is treated as a soft
constraint with explicit relaxations, and costs are reported as bands with assumptions. No LLM is used, output is byte-for-byte deterministic,
and the engine runs offline with the Python standard library.

## 2. Problem understanding and assumptions
- The judges reward right-for-the-constraints recommendations, good inputs and self-explanation, so the engine is built around explicit constraints
  and traceable reasons, not popularity.
- Scope decisions: one recommendation per scenario; frameworks (frontend/backend) are treated as software you host, services as managed products;
  the cost band is an order-of-magnitude estimate, not a quote.
- Assumptions applied by the engine are listed in each result's `assumptions` array (defaults, relaxed constraints, derived values).
- `project.description` is intentionally ignored by the engine so free text cannot change the stack (this also guarantees the "LLM-off" property).
- RBI localisation is interpreted as requiring Indian data residency; `data_residency: other` is treated as "hyperscaler or self-hosted only".

## 3. System architecture
Pipeline: validate -> derive features -> hard filters -> joint scoring over each viable hosting option -> warnings/cost/explanations -> JSON.
Modules: `validate.py` (validation and defaults), `kb.py` (knowledge base, region notes, lifecycle rules), `engine.py` (decision logic), `cli.py`,
`server.py` and `static/index.html` (interfaces). Technology: Python 3.11+ standard library only; HTML/CSS/vanilla JS for the UI.
Diagram: see the ASCII diagram in `README.md` (redraw it as a figure for the PDF).

## 4. Input design and research
Mandatory fields (all implemented, validated and defaulted as specified) and why they matter architecturally:
- `project.type` and `project.platforms`: decide whether a backend exists at all (content sites can be static), and which client frameworks can cover the platforms.
- `scale.*`: users after 12 months sets the scale tier (0-4) used for cost, caching, queues and scale caps; peak concurrency and traffic pattern drive bursts and websocket needs; workload and data volume steer the database choice.
- `team.*`: experience, size and DevOps set operations capacity (a penalty applies when a component's operations burden exceeds it); languages drive skill fit and the backend choice.
- `budget.monthly_infra_usd` and `timeline.mvp_weeks`: soft constraints that shift scores, defer optional components and trigger warnings.
- `infrastructure.*`: cloud preference, deployment model and data residency are hard constraints; existing systems are reused where supported and flagged when end-of-life.
- `requirements.*`: each requirement adds a supporting component or changes selection (realtime needs websocket hosting, offline needs a sync-capable store, SEO needs pre-rendering, payments need a gateway, and so on).
- `compliance`: PCI DSS, HIPAA, SOC 2 and ISO 27001 restrict managed services to vendors with recorded attestations; RBI forces India; GDPR/DPDP add notes.
- `priorities.*`: converted to weights over six rating dimensions.
Extra parameters added by this engine (each changes output and is validated): `extra.expected_rps`, `extra.geo_distribution`,
`extra.vendor_lock_in_tolerance`, `extra.existing_licences`, `extra.hiring_plan_6m`, `extra.data_sensitivity`, `extra.integration_needs`,
`extra.sync_conflict_tolerance`. Examples: expected requests per second raises the load tier and cost; a low lock-in tolerance penalises proprietary
managed services; restricted data sensitivity raises the security weight and penalises unattested vendors; hiring plans raise operations capacity;
strict consistency conflicts with offline-first writes and produces a warning.
Validation rules: types, ranges, enums, non-empty platforms, priorities 1-5, all errors reported together with field names, never a crash.
Research: sources are listed per knowledge-base entry and audited in `docs/KB_AUDIT.md`.

## 5. Knowledge base and decision logic
- Representation: each entry has layer, languages, regions, self-hosting and SaaS flags, cloud, ratings (time to market, cost, scalability,
  performance, maintainability, security; 1-5 author judgements), operations burden, comfortable scale cap, cost band (fixed + per-1k-users), tags,
  attestations, strengths, limits and sources. 123 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 62 supporting.
- Hard constraints filter candidates (cloud tag must match an explicit preference; deployment model must be satisfied; data residency requires a
  verified region or self-hosting; attestation sets must be covered; no Kubernetes without DevOps and a team of 4; websocket support for realtime).
- Soft scoring: weighted rating sum using priority weights, plus skill fit (a hard preference for backends in the team's languages), requirement and
  type bonuses, cloud affinity, existing-system reuse, scale and operations penalties, a cost penalty relative to the budget, and lock-in adjustments.
- Joint selection: for every viable hosting option the best backend, frontend, database and supporting services are chosen together, so incompatible
  combinations (self-managed databases on serverless platforms, cross-cloud data stores) lose; the best total wins; ties break by name.
- Conflicts: contradictions produce warnings with codes and severities; unsatisfiable hard constraints give `infeasible` with a critical warning;
  relaxed constraints are named in `assumptions`.
- Determinism: validation canonicalises list order; no randomness, clocks or iteration over unordered sets influence the result; ties are broken
  alphabetically. Tests check byte-for-byte stability, id/name/description independence and list-order independence.
- LLM usage declaration: none. There is no LLM switch to turn off because there is no LLM path.

## 6. Sample recommendations (take screenshots from the running UI; walk through at least P2 and P4)
Run `python -m stacksense run data/scenarios/<file> ...` for each public scenario (split the list file into six single-scenario files) and save
the results as `outputs/P1_output.json ... P6_output.json`. Current engine results (re-run before submission):
- P1 portfolio: Eleventy on GitHub Pages, no backend or database, estimated cost $0.
- P2 marketplace India: React Native (Expo) client for web+Android, NestJS on Google Cloud Run, Supabase Postgres in Mumbai, Razorpay, Firebase Authentication (phone OTP), Socket.IO, with an SEO limitation warning for the client-rendered web app.
- P3 whiteboard SaaS: Next.js, Go (Gin) on Google Cloud Run, Cloud SQL for PostgreSQL, Yjs for CRDT collaboration, Memorystore, Pub/Sub, Stripe.
- P4 lending India: React Native (Expo), Spring Boot on AWS ECS Fargate, Amazon RDS for PostgreSQL (Mumbai), Cognito, SageMaker, Razorpay, CloudFront, CloudWatch, with PCI DSS/RBI/DPDP/ISO 27001 notes.
- P5 internal HR tool: Blazor and ASP.NET Core on Azure App Service, reusing the on-premises SQL Server 2019 and Microsoft Entra ID, Azure Blob Storage.
- P6 offline crop survey: React Native (Expo) client, offline-capable Firestore (Mumbai) with a Django API on Google Cloud Run, Firebase phone OTP.
(Explain in the report why each component was chosen using the `driven_by`, `alternatives` and `what_would_change` fields.)

## 7. Edge-case handling (table for the report; add one screenshot per row)
| Category | Detection | Engine behaviour |
|---|---|---|
| Missing fields | validator finds absent required fields | `invalid_input` with every missing field named; optional fields default and are listed in assumptions |
| Invalid values | wrong type, negative, unknown enum, out-of-range priority | field-level `validation_errors`, `stack: null`, never a crash |
| Contradictions | e.g. 99.99% availability with a small beginner team, million users with a tiny budget, 2-week MVP on 3+ platforms, rbi_localisation with another residency | warnings with severity (critical when severe); `ok_with_warnings` with relaxations in assumptions, or `infeasible` |
| Over-engineering traps | tiny team, content-only site, high traffic but static | static or monolith styles; Kubernetes and microservices only with DevOps and a large team |
| Regulatory | HIPAA, PCI DSS, RBI, GDPR, DPDP, residency | only attested or self-hosted infrastructure, India-based gateways for India, compliance notes naming each regime |
| Existing systems | SQL Server, Entra ID, Microsoft 365, Okta, CRMs | reused (database) or integrated (identity), with notes explaining how |
| Restricted deployment | on_premise, air_gapped | self-hostable components only, no CDN or SaaS; payments flagged |
| Skill mismatch | languages with no matching backend | best overall fit plus a SKILL_MISMATCH warning explaining the trade-off |
| Deprecated technology | end-of-life items in `existing_systems` | never recommended; EOL_EXISTING_SYSTEM warning and migration note |

## 8. Validation
- Unit and property tests: determinism, order and id independence, hard-constraint invariants over fuzzed scenarios.
- A separate strict gate (`gate/`) checks the same properties from the outside, plus anti-hard-coding scans, schema checks and local sensitivity.
- Sanity checks against real-world practice (state in the report): static sites on free static hosts; Indian fintech on AWS Mumbai with a managed
  database and an Indian gateway; Microsoft shops on Azure with Entra ID; offline-first field apps on a sync-capable store.
- Optional extension for the report: compare against published engineering case studies (cite them if you add any).

## 9. Limitations and future work
- Ratings and costs are author estimates, not measurements; bands are order-of-magnitude.
- The knowledge base has 123 entries; many valid options (for example Kubernetes services, Neon, PlanetScale, Hetzner, Fly.io) are absent because their
  regions or lifecycle could not be verified within the time available.
- Vendor compliance attestations are taken from public programmes and recorded coarsely.
- Reuse detection of existing systems relies on name patterns; an on-premises Oracle estate cannot be reused because the KB has no Oracle entry.
- `on_premise` with payments is reported infeasible because no self-hostable payment processor exists.
- Future work: weights learned from public datasets (for example a developer survey), more regions per vendor, multi-region designs, cost models from live price APIs.

## 10. References and third-party tools
See the credits in `README.md` and the per-entry sources in `data/kb/*.json` and `docs/KB_AUDIT.md`. No third-party library, dataset or API is used at runtime.

## 11. AI assistance declaration
Claude Code (Anthropic) was used to write code, the knowledge-base tables, tests and documentation, and to run source verification scripts.
Design decisions, the decision logic, the knowledge-base content and the validation approach are the author's; the author reviewed and takes
responsibility for the code and data.
