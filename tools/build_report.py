"""Builds report/report.html from the repository's real outputs and screenshots, then prints it to PDF with headless Chrome.
Usage: python tools/build_report.py "<Full Name>" "<College>" "<Unstop email>" "<GitHub URL>" """
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
name, college, email, github = (sys.argv + ["<NAME>", "<COLLEGE>", "<UNSTOP EMAIL>", "<GITHUB>"][len(sys.argv) - 1:])[1:5]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
esc = html.escape
OUT = {sid: json.loads((ROOT / f"outputs/{sid}_output.json").read_text(encoding="utf-8")) for sid in ("P1", "P2", "P3", "P4", "P5", "P6")}
INP = {sid: json.loads((ROOT / f"outputs/inputs/{sid}.json").read_text(encoding="utf-8")) for sid in OUT}
kbn = {}
for f in (ROOT / "data/kb").glob("*.json"):
    for e in json.loads(f.read_text(encoding="utf-8")):
        kbn[e["layer"]] = kbn.get(e["layer"], 0) + 1
n_kb = sum(kbn.values())
n_support = n_kb - sum(kbn.get(k, 0) for k in ("frontend", "backend", "database", "hosting"))


def stack_row(sid):
    o = OUT[sid]
    st = o["stack"]
    c = o["estimated_monthly_cost_usd"]
    sup = ", ".join(x["choice"] for x in st["supporting"]) or "none"
    cost = f"${c['min']}" if c["min"] == c["max"] else f"${c['min']}-{c['max']}"
    warn = ", ".join(sorted({w["code"] for w in o["warnings"] if w["severity"] != "info"})) or "none"
    return (f"<tr><td><b>{sid}</b> {esc(INP[sid]['project']['name'])}</td><td>{esc(st['frontend']['choice'])}</td><td>{esc(st['backend']['choice'])}</td>"
            f"<td>{esc(st['database']['choice'])}</td><td>{esc(st['hosting']['choice'])}</td><td>{esc(sup)}</td><td>{cost}</td><td>{esc(o['status'])}<br><small>{esc(warn)}</small></td></tr>")


def first_sentences(text, n=2):
    parts = text.replace("\n", " ").split(". ")
    return ". ".join(parts[:n]).rstrip(".") + "."


def walkthrough(sid):
    o = OUT[sid]
    st = o["stack"]
    rows = []
    for layer in ("frontend", "backend", "database", "hosting"):
        c = st[layer]
        alt = c["alternatives"][0] if c["alternatives"] else None
        rows.append(f"<li><b>{layer}: {esc(c['choice'])}.</b> {esc(first_sentences(c['justification'], 2))} "
                    f"<i>Driven by:</i> {esc(', '.join(c['driven_by']))}." + (f" <i>Why not {esc(alt['choice'])}:</i> {esc(alt['why_not'])}" if alt else "") + "</li>")
    for c in st["supporting"]:
        rows.append(f"<li><b>{esc(c['layer'])}: {esc(c['choice'])}.</b> {esc(first_sentences(c['justification'], 1))}</li>")
    cst = o["estimated_monthly_cost_usd"]
    warn = "; ".join(f"{w['code']} ({w['severity']})" for w in o["warnings"]) or "none"
    return f"<ul class='wk'>{''.join(rows)}</ul><p><b>Cost band:</b> ${cst['min']}-{cst['max']}/month. <b>Warnings:</b> {esc(warn)}.</p>"


EDGE = [
    ("Missing fields", "edge_missing_fields", "R1-03: team.languages absent and an unknown deployment model. The engine returns invalid_input and names every offending field; optional fields that are merely absent are defaulted and listed under assumptions."),
    ("Invalid values", "edge_invalid_values", "R1-02: a string where an integer is required, a negative budget and an out-of-range priority are all reported together with field names; the stack is null and nothing crashes."),
    ("Contradictions", "edge_contradiction", "R1-05: 99.99% availability for a solo beginner on $30/month. A critical AVAILABILITY_VS_TEAM and a BUDGET_EXCEEDED warning are raised, the status is ok_with_warnings, and the assumptions state what was relaxed."),
    ("Over-engineering traps", "edge_overengineering", "R1-07: 8 million users on a content site with a $100 budget. The engine keeps it a static site on a CDN-backed host (no backend, database or Kubernetes) and warns that the budget works only because it is static."),
    ("Regulatory constraints", "edge_regulatory", "R1-11: PCI DSS + RBI localisation + DPDP on Azure in India. Only attested Indian-region Azure services and an India-based gateway are used; the compliance notes name each regime."),
    ("Restricted deployment", "edge_restricted", "R1-16: air-gapped internal tool. Only self-hostable components (Compose on a Linux VM, PostgreSQL, Keycloak, SeaweedFS, GitLab CI, Grafana): no SaaS, no CDN."),
    ("Skill mismatch", "edge_skill_mismatch", "R1-20: a team whose languages match no backend in the knowledge base. A mainstream framework is chosen, SKILL_MISMATCH explains the trade-off and the status is ok_with_warnings."),
    ("Deprecated technology", "edge_deprecated", "R1-14: existing Python 2.7, MySQL 5.7 and AngularJS. None is recommended or reused; EOL_EXISTING_SYSTEM is raised for each and the integration notes describe the migration."),
    ("Existing systems", "edge_existing", "R1-15 (end-of-life SQL Server 2012 and Windows Server 2012 R2 are flagged and replaced). For reuse of a supported system see P5: the on-premises SQL Server 2019 is kept and Entra ID is reused."),
]
edge_html = "".join(f"<div class='edge'><p><b>{a}.</b> {esc(c)}</p><img src='screenshots/{b}.png'></div>" for a, b, c in EDGE)
appendix = "".join(f"<div class='full'><h3>{sid}: {esc(INP[sid]['project']['name'])}</h3><img src='screenshots/{sid}_full.png'></div>" for sid in OUT)

css = """
@page{size:A4;margin:16mm 15mm 16mm 15mm}
body{font:9.6pt/1.38 'Segoe UI',Arial,sans-serif;color:#16202a}
h1{font-size:25pt;margin:0 0 6pt}h2{font-size:13.5pt;margin:13pt 0 4pt;border-bottom:1.4px solid #0b6bcb;padding-bottom:2pt;color:#0b4a8f}
h3{font-size:10.5pt;margin:8pt 0 3pt}p{margin:3pt 0}ul{margin:3pt 0 3pt 15pt;padding:0}li{margin:1.5pt 0}
table{border-collapse:collapse;width:100%;margin:4pt 0;font-size:8.4pt}th,td{border:1px solid #cfd6dd;padding:2.5pt 4pt;vertical-align:top;text-align:left}th{background:#eaf1f9}
small{color:#5b6773}code{font:8.4pt Consolas,monospace;background:#f1f4f7;padding:0 2pt}
.title{page-break-after:always;padding-top:70mm}.title .sub{font-size:13pt;color:#4a5866;margin-bottom:22pt}.title table{width:75%;font-size:10.5pt}
.diagram{display:flex;gap:4pt;align-items:stretch;margin:6pt 0}.diagram div{flex:1;border:1.2px solid #0b6bcb;border-radius:5pt;padding:4pt;font-size:8pt;background:#f2f7fd}.diagram .arrow{flex:0 0 10pt;border:0;background:none;text-align:center;font-size:12pt;padding-top:14pt}
.edge{break-inside:avoid;margin:5pt 0}.edge img{width:11.2cm;border:1px solid #cfd6dd;display:block;margin-top:2pt}.top img{width:12.3cm;border:1px solid #cfd6dd}
.full{break-inside:auto;margin-top:6pt}.full img{width:10.8cm;border:1px solid #cfd6dd}.wk li{margin:2pt 0}.pb{page-break-before:always}
"""

body = f"""
<div class='title'><h1>StackSense Challenge</h1><div class='sub'>Synergy '26 &middot; Online systems-design challenge &middot; Intelligent tech stack recommendation engine<br>Project report</div>
<table><tr><th>Name</th><td>{esc(name)}</td></tr><tr><th>College</th><td>{esc(college)}</td></tr><tr><th>Unstop registered email</th><td>{esc(email)}</td></tr>
<tr><th>GitHub</th><td>{esc(github)}</td></tr><tr><th>Date</th><td>November 2026</td></tr><tr><th>Engine version</th><td>1.0.0 (Python 3.11+, standard library only)</td></tr></table></div>

<h2>1. Abstract</h2>
<p>StackSense is a deterministic tech-stack recommendation engine. It validates a scenario, derives features (load tier, operations capacity, priority weights),
removes every option that breaks a hard constraint (data residency, compliance, deployment model, explicit cloud preference) from a curated, cited
{n_kb}-entry knowledge base, and jointly scores hosting, backend, frontend, database and supporting services. Every component comes with the input fields that
drove it, alternatives with the reason they lost, trade-offs and what-would-change counterfactuals. Contradictions become severity-labelled warnings, the budget
is a soft constraint with explicit relaxations, and cost is a band with assumptions. No LLM is used, output is byte-for-byte deterministic, and the engine runs
offline from the Python standard library.</p>

<h2>2. Problem understanding and assumptions</h2>
<p>The judges reward stacks that are right for the constraints, inputs that capture what drives architecture, and explanations a senior engineer would accept, so the
engine is built around explicit constraints and traceable reasons rather than popularity. <b>Scope decisions:</b> one recommendation per scenario; frameworks (frontend/backend)
are software you host, while hosting, databases and supporting layers are services or self-managed products; the cost output is an order-of-magnitude band, not a quote.
<b>Interpretations:</b> <code>project.description</code> is intentionally ignored by the engine (so free text can never change the stack and the LLM-off requirement holds trivially);
RBI localisation implies Indian data residency, and when it conflicts with another residency both constraints must be satisfied or the result is infeasible;
<code>data_residency: other</code> allows only hyperscaler or self-hosted options. Every default and every relaxed constraint is listed in <code>assumptions</code>.</p>

<h2>3. System architecture</h2>
<div class='diagram'><div><b>Input</b><br>CLI, web UI or API: scenario JSON</div><div class='arrow'>&rarr;</div><div><b>validate.py</b><br>types, ranges, enums, all errors at once; defaults &rarr; assumptions</div><div class='arrow'>&rarr;</div>
<div><b>Features</b><br>load tier, ops capacity, priority weights, effective residency</div><div class='arrow'>&rarr;</div><div><b>Hard filters</b><br>cloud, deployment, residency, compliance, runtimes, realtime</div><div class='arrow'>&rarr;</div>
<div><b>Joint scoring</b><br>per hosting option: best backend, frontend, database, supporting</div><div class='arrow'>&rarr;</div><div><b>Output</b><br>stack, warnings, cost band, notes</div></div>
<p>The knowledge base (<code>data/kb/*.json</code>) feeds the filters and the scorer. Modules: <code>validate.py</code> (validation and defaults), <code>kb.py</code> (knowledge base, region notes, end-of-life rules),
<code>engine.py</code> (features, filters, scoring, joint selection, warnings, cost, explanations), <code>cli.py</code>, <code>server.py</code> and <code>static/index.html</code> (interfaces).
<b>Data flow:</b> raw JSON &rarr; normalised scenario plus assumptions &rarr; features &rarr; for each hosting option that passes the hard constraints the engine builds the best backend, frontend,
database and supporting services for that host (so cloud affinity, runtime fit, websocket support and self-hosting rules hold together), scores the whole stack and keeps the best; ties break alphabetically.
<b>Technology:</b> Python 3.11+ standard library only (<code>json, re, http.server, argparse, unittest</code>); the UI is one offline HTML page with vanilla JavaScript. No framework, build step or network call at run time.</p>

<h2>4. Input design and research</h2>
<p>All mandatory fields are implemented exactly as specified (types, ranges, enums, defaults recorded in <code>assumptions</code>). Why each group matters architecturally:</p>
<table><tr><th>Inputs</th><th>Architectural effect</th><th>Validation</th></tr>
<tr><td><code>project.type</code>, <code>project.platforms</code></td><td>Whether a backend exists at all (content sites can be static); which client frameworks cover the platforms (Expo/Flutter vs native vs web only)</td><td>enum; non-empty list of known platforms</td></tr>
<tr><td><code>scale.*</code></td><td>Load tier 0-4 (12-month users, peak concurrency, expected rps) drives caching, queues, CDN, cost and scale-cap penalties; workload and data volume steer the database; traffic pattern raises the cost upper bound</td><td>integers &ge; 0, enums; peak above users and launch above 12-month users produce info warnings</td></tr>
<tr><td><code>team.*</code></td><td>Experience, size and DevOps set operations capacity; languages decide the backend (a hard preference for matching frameworks, SKILL_MISMATCH otherwise); Kubernetes only with DevOps and 4+ engineers</td><td>size &ge; 1, enum experience, lower-cased language list</td></tr>
<tr><td><code>budget</code>, <code>timeline</code></td><td>Soft constraints: cost penalty, deferral of optional components, warnings (million users on a tiny budget, 2-week MVP on three platforms)</td><td>budget &ge; 0, weeks &ge; 1</td></tr>
<tr><td><code>infrastructure.*</code></td><td>Cloud preference, deployment model and data residency are hard constraints; existing systems are reused (supported databases, identity providers) or flagged when end-of-life</td><td>enums; string list</td></tr>
<tr><td><code>requirements.*</code></td><td>Each adds a component or changes selection: realtime needs websocket hosting and a realtime layer; offline needs a sync-capable store; SEO needs pre-rendering; payments need a gateway (India-based for India); auth type picks the identity service; ML picks inference, retrieval or training components; availability and p95 add warnings</td><td>booleans, enums, availability in {{99, 99.9, 99.95, 99.99}}, p95 &gt; 0 or null</td></tr>
<tr><td><code>compliance</code>, <code>priorities.*</code></td><td>PCI DSS, HIPAA, SOC 2 and ISO 27001 limit managed services to vendors with recorded attestations (and, for HIPAA/PCI, exclude unattested SaaS); RBI forces India; priorities (1-5) become weights over six rating dimensions</td><td>enum list; integers 1-5</td></tr></table>
<p><b>Extra parameters added by this engine</b> (all validated, all change recommendations or warnings, all defaulted and recorded when absent):
<code>extra.expected_rps</code> raises the load tier and cost; <code>extra.geo_distribution</code> adds a CDN for regional/global users;
<code>extra.vendor_lock_in_tolerance</code> penalises proprietary-API services when low; <code>extra.existing_licences</code> biases towards licences already paid for (and warns when a licence cannot be used);
<code>extra.hiring_plan_6m</code> raises operations capacity; <code>extra.data_sensitivity</code> raises the security weight and penalises unattested vendors;
<code>extra.integration_needs</code> adds queues for ERP/CRM/SMS integrations; <code>extra.sync_conflict_tolerance</code> reconciles offline writes with consistency needs (strict consistency conflicts with offline-first and is warned).
<b>Research:</b> the knowledge base cites official documentation and pricing pages per entry; region availability for AWS, Azure, Google Cloud, DigitalOcean, Vercel, Render, Supabase, Firestore and MongoDB Atlas was read from the vendors' region pages on 13 November 2026,
open-source project lifecycle was checked through the GitHub API (this removed MinIO, whose open-source repository is no longer maintained), and every source URL was opened and logged (<code>docs/KB_AUDIT.md</code>).</p>

<h2>5. Knowledge base and decision logic</h2>
<p><b>Representation.</b> {n_kb} entries: {kbn.get('frontend', 0)} frontend, {kbn.get('backend', 0)} backend, {kbn.get('database', 0)} database, {kbn.get('hosting', 0)} hosting and {n_support} supporting (cache, queue, search, auth, storage, CDN, realtime, payments, ML, CI/CD, observability).
Each entry records languages, regions, self-hostable/SaaS flags, cloud, hosting type and runtimes, six 1-5 ratings (time to market, cost, scalability, performance, maintainability, security: curated author judgements), operations burden, comfortable scale cap, a fixed plus per-1,000-user cost band, tags, attestations, strengths, limits and source URLs.</p>
<p><b>Hard constraints</b> remove candidates: an explicit cloud preference needs a host of that cloud; the deployment model must be satisfied (air-gapped and on-premises allow self-hostable components only, no CDN or SaaS); data residency needs a verified region or self-hosting (a conflicting pair such as RBI plus EU must satisfy both); attestation sets must be covered; realtime needs websocket hosting;
Kubernetes-class platforms need DevOps and four engineers; self-managed databases need persistent machines; static hosts run no server components.
<b>Soft scoring</b> is a weighted rating sum using the priority weights, plus skill fit, requirement and type bonuses, cloud affinity, existing-system reuse, penalties for operations burden beyond capacity, scale beyond a component's range and cost relative to the budget, and lock-in adjustments.
<b>Joint selection:</b> for every viable hosting option the engine builds the best backend, frontend, database and supporting services, so incompatible combinations (a self-managed database on a serverless host, cross-cloud data stores) lose; the best total wins.
<b>Conflicts:</b> contradictions raise warnings with codes and severities, unsatisfiable hard constraints give <code>infeasible</code> with a critical warning, and relaxed constraints are named in <code>assumptions</code>; when the estimate is far above the budget, optional components are deferred most-expensive-first.
<b>Determinism:</b> list inputs are canonicalised, no randomness or clock is used, ties break alphabetically; tests check byte-for-byte stability and independence from scenario id, name, description and list order.
<b>LLM usage declaration:</b> none. The engine contains no LLM call, so there is no switch to turn off, and the stack is identical with or without any LLM configuration (tested with the network blocked).</p>

<h2>6. Sample recommendations</h2>
<p>All six public scenarios were run through the web UI (screenshots in Appendix A, taken from the running engine; JSON in <code>outputs/</code>). Summary:</p>
<table><tr><th>Scenario</th><th>Frontend</th><th>Backend</th><th>Database</th><th>Hosting</th><th>Supporting</th><th>Cost/mo</th><th>Status</th></tr>{''.join(stack_row(s) for s in OUT)}</table>
<h3>In-depth: P2 FixIt Now (home-services marketplace, India)</h3>
<p>3 intermediate engineers (JavaScript, TypeScript, Python), $150/month, DPDP and Indian residency, realtime chat, payments, phone OTP, search, uploads, SEO, 99.9%, p95 500 ms.</p>
{walkthrough('P2')}
<div class='top'><img src='screenshots/P2_top.png'></div>
<h3>In-depth: P4 QuickCredit (digital lending, India)</h3>
<p>8 senior engineers (Java, Kotlin, TypeScript) with DevOps, $6,000/month, AWS only, RBI localisation + PCI DSS + DPDP + ISO 27001, UPI payments, KYC uploads, credit-scoring inference, 99.95%, p95 300 ms.</p>
{walkthrough('P4')}
<div class='top'><img src='screenshots/P4_top.png'></div>
<p>P1, P3, P5 and P6 follow the same logic: P1 is a static site on a free host because nothing needs a server; P3 combines a CRDT library (Yjs) with a websocket-capable container host, caching and a global payment gateway; P5 reuses the supported on-premises SQL Server 2019 and Entra ID inside Azure; P6 picks an offline-sync database (Firestore, Mumbai) because the field devices lose connectivity.</p>

<h2>7. Edge-case handling</h2>
<p>Each row is a real run through the UI (warnings and notes view). Detection is rule-based on the validated input; none of the behaviours is keyed on scenario names.</p>
{edge_html}

<h2>8. Validation</h2>
<p><b>Automated tests:</b> 132 unit and property tests (<code>python -m unittest discover -s tests</code>): validation rules, determinism, order/id/description independence, hard-constraint invariants over fuzzed scenarios, CLI and web API behaviour, and a regression test for every defect found in review.
<b>Independent gate</b> (<code>gate/run_gate.py</code>, written separately from the engine and kept unmodified during the build): public scenarios, byte-identical reruns across hash seeds, independence from id/name/description, LLM-off and no-network runs, anti-hard-coding scans, 21 invalid-input cases, minimal-input defaults, contradiction and hard-constraint cases, extras that must change output, 120 fuzzed scenarios (hard constraints, diversity, skill fit, templated-text detection), local sensitivity, web UI, documentation, and protected-file integrity.
<b>Adversarial review:</b> 127 hand-designed scenarios in six rounds (invalid inputs, contradictions, over-engineering traps, regulated systems, legacy/EOL systems, air-gapped and on-premises, skill mismatches, offline-first, realtime at scale, ML/LLM, extreme budgets, extras-heavy files, and modified versions of the public scenarios), about 9,000 fuzzed scenarios scanned for known-bad patterns, and 6,000 malformed inputs (0 crashes). Each output was read critically and every defect fixed at its root cause (examples: a scoring bug that rewarded stacks for having more components, .NET-only libraries recommended to non-.NET teams, SQLite on ephemeral containers, unattested SaaS under HIPAA).
Defects per hand-written round were roughly 12, 6, 5, 1, 3 and 1, so the engine stabilised but review never reached a formally clean round. <b>Sanity checks:</b> outputs were compared by the author with common industry patterns (static sites on free CDN hosts, Indian fintech on a hyperscaler's Mumbai region with an Indian gateway, Microsoft shops on Azure with Entra ID, offline field apps on sync-capable stores); no formal comparison with published case studies was done.</p>

<h2>9. Limitations and future work</h2>
<ul><li>Ratings and costs are author estimates, not measurements; cost bands are order-of-magnitude. Vendor compliance attestations are recorded coarsely from public programmes and were not verified claim by claim; EU/US regions of several vendors are general knowledge.</li>
<li>The knowledge base is finite ({n_kb} entries): no media pipelines, and few niche or regional vendors; Neon, PlanetScale, Hetzner, Fly.io and CockroachDB are absent because their regions or lifecycle could not be verified in time.</li>
<li>Reuse of existing systems relies on name patterns; an on-premises Oracle estate cannot be reused (no Oracle entry).</li>
<li><code>on_premise</code> combined with payments is reported infeasible because no self-hostable payment processor exists (documented in <code>GATE_ISSUES.md</code>).</li>
<li>The Docker image was built and run once on the development machine (UI and API answered); it was not tested on other platforms.</li>
<li><b>Future work:</b> weights learned from public developer surveys, more regions and multi-region designs, live price APIs for the cost model, a larger audited knowledge base.</li></ul>

<h2>10. References and third-party tools</h2>
<p>No third-party library, dataset or API is used at run time. Knowledge-base facts come from the vendors' official documentation, pricing and region pages linked per entry in <code>data/kb/*.json</code> and listed in <code>docs/KB_AUDIT.md</code>
(AWS, Microsoft Azure, Google Cloud, DigitalOcean, Vercel, Render, Supabase, Firebase/Firestore, MongoDB, Cloudflare, Netlify, GitHub, Razorpay, Cashfree, PayU, Stripe, Adyen, Auth0, Algolia and the open-source project sites).
Open-source project lifecycle was checked with the public GitHub API. Region pages read on 13 November 2026: AWS Regions, Azure region list, Google Compute Engine regions and zones, DigitalOcean regional availability, Vercel regions, Render regions, Supabase regions, Cloud Firestore locations and MongoDB Atlas on AWS.</p>

<h2>11. AI assistance declaration</h2>
<p>Claude Code (Anthropic) was used to write code, the knowledge-base tables, tests, documentation and this report, to run source-verification scripts, and to take the screenshots with a headless browser. The problem interpretation, the decision logic, the knowledge-base content and the validation approach are the author's; the author is responsible for the submission.
No LLM is part of the engine.</p>

<h2 class='pb'>Appendix A. Full screenshots of the six public scenarios (real runs of the web UI)</h2>
{appendix}
"""

doc = f"<!doctype html><html><head><meta charset='utf-8'><title>StackSense report</title><style>{css}</style></head><body>{body}</body></html>"
(ROOT / "report").mkdir(exist_ok=True)
hp = ROOT / "report" / "report.html"
hp.write_text(doc, encoding="utf-8")
pdf = ROOT / "report" / "report.pdf"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", hp.as_uri()], capture_output=True, timeout=180)
print(hp, pdf, pdf.exists() and pdf.stat().st_size)
