# Round 1 critique (skeptical architect + judge)

32 hand-designed scenarios (`scenarios.json`, outputs in `summary.md`). Classes: invalid (3), contradictions (3), over-engineering traps (3),
regulated (4), legacy/EOL (2), on_premise/air_gapped/VM (3), skill mismatch (2), offline-first (2), realtime at scale (2), ML/LLM (2),
extreme budgets (2), minimal-field (2), extras-heavy (2). The independent oracle found 0 violations; the problems below were found by reading
the outputs, which is what a judge's "known-bad choices" list would catch. Every defect was fixed at the root cause and has a regression test in
`tests/test_regression.py`.

| # | Scenario(s) | Defect found | Root cause | Fix |
|---|---|---|---|---|
| 1 | R1-04, 08, 09, 10, 19, 23, 24, 28, 31 | Firestore/DynamoDB chosen for relational workloads (internal tool with SSO, multi-tenant SaaS, HIPAA app, payments) | document/key-value stores scored well on cost/scale ratings with no relational-integrity preference | non-relational penalty unless offline, gaming/social/IoT, very write-heavy or realtime; extra penalty for multi-tenant, search, internal tools, SaaS, healthtech; relational bonus for typical app types |
| 2 | R1-04, 16, 17, 22, 26, 31 | "ASP.NET Core Identity" (a .NET library) recommended to Python/Node/Java teams | library components were not checked against the chosen backend language | hard compatibility filter: libraries must match the backend language (client libraries also the frontend), pgvector requires a PostgreSQL-family database, BullMQ requires a Node backend |
| 3 | R1-08, 10, 12, 16, 23 | Astro (a content-site generator) recommended for interactive apps (HIPAA app, ecommerce, internal tool, game) | no penalty for content-first generators on dynamic applications | penalty for static/SSG-only frameworks when the project is dynamic and not a content site |
| 4 | R1-14 | existing "MySQL 5.7" was reused although it is end of life, and was not flagged | lifecycle rules lacked database versions | added MySQL 5.x, MongoDB <=4.x and PostgreSQL <=13 rules; EOL databases are neither reused nor silently ignored |
| 5 | R1-21 | CDN recommended for an Android-only app | CDN rule ignored platforms | CDN only when the web platform is present or users are geographically distributed |
| 6 | R1-25 | LLM-RAG app had only a vector extension and no model-serving component | single ML slot per scenario | llm_rag now yields two ML components (retrieval + generation) with role-specific candidates |
| 7 | R1-26 | on-prem model training got ONNX Runtime (inference only) | no trainable framework available on-prem | added PyTorch to the KB (source opened, repository lifecycle checked); training prefers trainable components |
| 8 | R1-07 | "SCALE_VS_BUDGET: critical: cannot serve 8M users on $100" for a static site that is actually nearly free | warning ignored the static-site exception from the problem statement's over-engineering traps | severity warning with an honest message for static-like sites; Cloudflare Pages cost band corrected (free bandwidth) |
| 9 | R1-27 | $0-budget dynamic app landed on Azure App Service (about $13+) | budget-zero penalty was flat for any non-free entry | graded penalty by minimum/maximum cost, so Cloud Run style free tiers win |
| 10 | R1-31, R1-32 | extra licences "Microsoft 365"/"Oracle" ignored | case-sensitive matching | licences lower-cased; Oracle licence now produces LICENCE_NOT_USED |
| 11 | R1-31 | extra.vendor_lock_in_tolerance=low barely changed the result | flat penalty for all managed services | proprietary-API services (Firestore, DynamoDB, Lambda, Pub/Sub...) penalised far more than managed open-standard services |
| 12 | R1-17 | single Docker Compose VM recommended for 200,000 users without comment | scale cap penalty too small, no warning | stronger scale-cap penalty and a SINGLE_NODE_CAPACITY warning |
| 13 | P2 and others | wording: "a intermediate team", "$0-0/month", "self-managed store" for a managed service | text templates | article helper, money formatter, managed vs self-managed phrase |

## Remaining issues found (not fixed, documented as limitations)
- R1-28 (40M users, payments): Firestore/Cloud SQL are stretched; the KB has no globally distributed SQL (Spanner, CockroachDB) or Kubernetes services.
- R1-20 (unknown languages): ASP.NET Core is picked as the "best overall" mismatch backend; a more popular general-purpose framework would be a better default.
- R1-30 (analytics, managed cloud): ClickHouse/TimescaleDB are excluded on managed platforms because they need VMs, so analytics apps get a general relational database.
- Costs are order-of-magnitude estimates and may be off for individual components.
