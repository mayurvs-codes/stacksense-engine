# Round 10 critique (final round: 10 scenarios aimed at the newest KB entries and high-scale combinations)

Oracle: 0 violations. Scenarios: Kubernetes justified at 6M users with 15 engineers, 40M-user global fintech needing distributed SQL (Spanner chosen), offline C# desktop+Android POS (.NET MAUI chosen with an honest OFFLINE_SYNC_CUSTOM warning),
a small senior Go team (no Kubernetes), Azure API at 120k concurrent users, EU SaaS on AWS (EKS chosen with an explicit justification), $0 student project, IoT on AWS,
India social network at 9M users, on-premises government tool (k3s).

One defect found (fixed, regression-tested): R10-02 recommended an HTMX server-rendered front end for a 40M-user, 900k-concurrent public fintech app. HTMX is now excluded
for public applications at the highest load tiers (internal tools stay eligible) and for realtime apps above the smallest tier.

Not changed (documented): R10-05 (5M users, 120k concurrent, 12 engineers on Azure) is served by App Service rather than AKS, which is defensible but not the only valid answer; R10-08 has no
IoT-specific ingestion service (not in the KB). After the fix: fuzz scans (seeds 6001-6003, 1,800 scenarios) 0 oracle violations; robustness fuzz (3,000 malformed inputs) 0 crashes.
