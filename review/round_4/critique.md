# Round 4 critique (25 hand-designed edge scenarios, `tools/review_scenarios_r4.py`)

Mixed constraints: air-gapped RAG, on-premise Kubernetes SaaS, PCI-only shop, HIPAA in India on GCP, residency "other", cloud none + VM,
DPDP+RBI marketplace, iOS-only solo app, desktop+web, 30M-user static site, 99.99% with a strong team, SAP/AD, MongoDB 4.2, MySQL 8, restricted data,
8,000 rps API, hiring plan, Microsoft licences, ERP/CRM integration, merge-style offline sync, tiny realtime app, on-prem analytics, near-empty
scenario, every requirement flag at once. Oracle: 0 violations. Defects found by reading outputs (all fixed, regression tests added):

| # | Scenario | Defect | Root cause | Fix |
|---|---|---|---|---|
| 1 | R4-10 | static site with 30M users got Google Cloud Run, estimate $6k-49k and a critical budget warning | the stack total added a positive score for every supporting component, so stacks with more components (Cloud Run needs CI/CD and a CDN, static hosts need none) beat the free static host; also Cloudflare Pages' scale cap was too low | supporting components now count relative to a neutral score (never a bonus for merely existing); Cloudflare Pages cap raised; result Cloudflare Pages at $0-36 |
| 2 | scoring change side effect | Django on Azure Static Web Apps (found by a regression test after fix 1) | static hosts accepted any backend whose runtime name matched their managed-functions list | static hosts only accept "no backend" |
| 3 | R4-14 | existing MongoDB 4.2 (EOL) was abandoned for Azure SQL Database | EOL engines were simply ignored | EOL databases are flagged AND the same engine on a current managed version gets an upgrade bonus (MongoDB Atlas) |
| 4 | R4-04 | HIPAA workload used Firebase Authentication (no recorded attestation) | attestation rules covered only hosting/database/storage/ML | under HIPAA/PCI, SaaS auth/search/observability/realtime/queue/cache vendors without a recorded attestation are excluded; the note now says to confirm each service is inside the provider's BAA scope |
| 5 | fuzz seed 8888 (oracle) | RBI + data_residency "other": Supabase chosen (India yes, "other" no) | the engine kept only the overriding constraint | a conflicting pair must satisfy BOTH constraints; otherwise honest infeasibility |
| 6 | fuzz scans | Firestore edged out Cloud SQL for fintech/payments on score ties | no penalty for non-ACID stores in money flows | extra penalty for document/key-value stores with payments or fintech/ecommerce/marketplace types |
