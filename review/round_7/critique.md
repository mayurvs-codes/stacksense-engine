# Round 7 critique (15 fresh hand-written scenarios, `tools/review_scenarios_r7.py`)

Oracle: 0 violations. Scenarios: HIPAA+GDPR on GCP in the EU, AWS VM with low lock-in, Azure India fintech (RBI+PCI), on-prem docs site with search,
offline iOS app, backend-only game, NGO forms in India, enterprise SaaS (low lock-in, restricted data, global), legacy PHP 5.6/MySQL 5.5, on-prem
API at 3M users and 99.99%, India LLM app, offline desktop POS with SQL Server, spiky ticketing on $300, cloud none + air-gapped, India marketplace on VMs.
Three defects found, fixed, regression-tested:

| # | Scenario | Defect | Root cause | Fix |
|---|---|---|---|---|
| 1 | R7-04 | an on-premises docs site with search got Django + SQLite (over-engineered) | full-text search forced a backend even for content sites | content sites with only search stay static; a search service is added (Meilisearch on-prem, Algolia for SaaS) |
| 2 | R7-01 | telemedicine with realtime and 120k users got an HTMX front end | HTMX penalised but still won for non-JS teams | HTMX is excluded for realtime apps above the smallest load tier |
| 3 | R7-02, R7-08 | extra.vendor_lock_in_tolerance=low still chose Cognito/Auth0/Entra ID; Keycloak was penalised because its tags lacked social/email sign-in | lock-in penalty too weak, identity vendors not marked proprietary, KB tags incomplete | stronger proprietary-API penalty, Auth0/Entra ID marked proprietary, Keycloak tagged for social and email sign-in; low lock-in now selects Keycloak |

Remaining (documented): R7-12 recommends Flutter + Firestore for an offline C# desktop POS (the KB has no .NET MAUI/WPF-style client and Firestore's offline
persistence on desktop is limited); R7-05's Swift-only team needs a backend language it lacks (SKILL_MISMATCH stated).
Fuzz scans after the fixes (seeds 424242, 31, 600): 0 oracle violations; only the known borderline Firestore heuristic.
