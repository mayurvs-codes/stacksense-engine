# Round 2 critique (skeptical architect + judge)

25 new hand-designed scenarios (`tools/review_scenarios_r2.py`, outputs in `summary.md`): hobby site, Indian shop and SaaS under DPDP, telemedicine under
HIPAA+GDPR in the EU, IoT fleet on VMs, video social network, 40 ms API, ERP/SAP integration, air-gapped government tool, India chat app,
LLM tutor on AWS, EU fintech on Azure under PCI/GDPR/SOC 2, gaming, NGO donation site, offline desktop app, BI platform, GCP-mandated marketplace,
solo 3-week MVP, modernisation with Okta/Salesforce/PostgreSQL, low lock-in SaaS, India healthtech, India ticketing under RBI, on-premises wiki,
offline kiosk, ML training on GCP. The independent oracle found 0 violations. Reading the outputs found these defects (all fixed at the root cause,
each with a regression test in `tests/test_regression.py`):

| # | Scenario | Defect | Root cause | Fix |
|---|---|---|---|---|
| 1 | R2-05 | IoT fleet with 100,000 concurrent devices got no queue/ingestion layer | the load tier looked at 12-month users only | tier now also considers peak concurrency (and expected rps) |
| 2 | R2-18 | SQLite recommended on Cloud Run (ephemeral disk: data loss) | SQLite was allowed on container/PaaS hosts | SQLite only on VMs/on-premises servers |
| 3 | R2-12 | Azure estate got self-hosted Redis because no managed Azure cache existed | KB gap | added Azure Managed Redis (page opened and read, KB entry audited) |
| 4 | R2-02/03/05/08/20/21/22/25 | HTMX chosen as the UI for realtime, social, very high-scale and B2B apps | no penalty for HTMX at scale/realtime | penalties for tier>=3, realtime and social/gaming/collab types |
| 5 | R2-20 | low lock-in SaaS pushed to SaaS identity because self-hosted services on container hosts were penalised like serverless | one penalty for all non-library self-hosted services | container hosts only -0.5 (a container can run another container); serverless/PaaS/static keep -1.5 |
| 6 | R2-14, R2-18, zero-budget cases | $0-budget apps showed cost bands of 40-65 USD | CI/CD and Supabase fixed bands too pessimistic | recalibrated Supabase (free tier / $25 Pro), Cloud Build, CodePipeline, Azure Pipelines, GitHub Actions |

## Remaining issues (documented, not fixed)
- R2-06 (video, 2M users): no media-transcoding/streaming component exists in the KB.
- R2-19: Auth0 is recommended next to an existing Okta tenant; federating the existing Okta directly would also be valid.
- Knowledge-base ratings and cost bands remain author estimates.
