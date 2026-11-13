# Round 8 critique (15 modified versions of the public scenarios, `tools/review_scenarios_r8.py`)

The judges said they would run modified public scenarios, so each public scenario was changed along the axes that should change the answer: budget up or
x10, residency removed or added, cloud pinned (AWS, Azure, GCP), team shrunk, DevOps removed, languages changed, compliance changed, platforms added,
offline switched off, strict sync consistency, on-premise deployment, EOL SQL Server. Oracle: 0 violations. All 15 changes moved the stack in the expected,
local way (for example P4+Azure gives ASP.NET Core/Azure SQL, P5+on-prem keeps and reuses SQL Server and swaps Entra ID for Keycloak, P6 without offline drops Firestore
for a relational database, P3+India switches the gateway to Razorpay).

One defect found (fixed, regression-tested): R8-02 (portfolio + full-text search + EU) got Meilisearch, a server, on GitHub Pages, which cannot run it.
Cause: self-hosted services were only penalised, not forbidden, on static hosts, and the KB had no serverless search option.
Fix: static hosts cannot run server components; added Pagefind (static client-side search, source page opened, repository lifecycle checked) which is only used
when there is no backend.
