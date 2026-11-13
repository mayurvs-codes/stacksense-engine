# Round 6 critique (15 fresh hand-written scenarios after the round 4/5 fixes, `tools/review_scenarios_r6.py`)

Oracle: 0 violations. Read critically: blog in India, EU CRM SaaS on Azure, India ride-hailing under DPDP+RBI, on-prem lab tool, air-gapped bank,
seasonal ecommerce, vision ML on AWS, EU news site with accounts, on-prem IoT edge, India kids' education, GCP HR tool, billing API, offline POS,
tiny all-features app, 15M-user social network. 14 of 15 outputs judged defensible.

Defect found (fixed, regression test added): R6-05 (99.95% availability on a single on-premises Docker Compose host) produced no availability warning,
because the single-node warning covered only cloud VMs. It now covers on-premises single servers (not Kubernetes).

Not changed (documented): R6-08 shows a critical budget warning for 900,000 users on $200 (cost model is pessimistic for read-heavy sites but the
warning is directionally right); R6-13 recommends Flutter for a JavaScript team because it is the only framework covering desktop plus Android (skill
trade-off stated in its justification).
