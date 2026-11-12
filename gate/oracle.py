"""Independent rule oracle for StackSense outputs.

Written by the project owner's reviewer session, NOT by the build agent.
It encodes hard constraints, known-bad choices and expected warnings that
must hold for ANY input (public, hidden or fuzzed). Stdlib only.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ["frontend", "backend", "database", "hosting"]

STD_PATHS = {
    "project.name", "project.type", "project.description", "project.platforms",
    "scale.users_at_launch", "scale.users_12_months", "scale.peak_concurrent_users",
    "scale.traffic_pattern", "scale.workload", "scale.data_volume_gb_12_months",
    "team.size", "team.experience", "team.languages", "team.has_devops",
    "budget.monthly_infra_usd", "timeline.mvp_weeks",
    "infrastructure.cloud_preference", "infrastructure.deployment_model",
    "infrastructure.data_residency", "infrastructure.existing_systems",
    "requirements.realtime", "requirements.offline_support", "requirements.full_text_search",
    "requirements.file_media_storage", "requirements.payments", "requirements.auth",
    "requirements.multi_tenant", "requirements.ml_features", "requirements.seo_critical",
    "requirements.availability", "requirements.p95_latency_ms", "compliance",
}
PRIORITY_KEYS = ["cost", "time_to_market", "scalability", "performance", "maintainability", "security"]
for _k in PRIORITY_KEYS:
    STD_PATHS.add("priorities." + _k)

DEPRECATED = [
    r"angularjs", r"angular\.js", r"parse\.com", r"heroku free", r"gatsby cloud",
    r"iot core", r"dynamic links", r"centos (7|8)\b", r"windows server 20(03|08|12)\b",
    r"sql server 20(05|08|12|14|16)\b", r"\.net (core )?(1|2|3\.1|5|6|7)\b",
    r"python ?2(\.\d+)?\b", r"python 3\.[0-8]\b", r"node(\.js)? ?(0|1[0-8]|[2-9])\b",
    r"php ?[4-7]\b", r"xamarin", r"atlas device sync", r"realm sync", r"mongodb realm",
    r"qldb", r"codecommit", r"cloud source repositories", r"\bmesos\b", r"\bsilverlight\b",
    r"\bflash\b", r"\bcoreos\b", r"\bbower\b",
]
EOL_WARNING_CODE = re.compile(r"EOL|END_OF_LIFE|DEPRECAT|LEGACY|UNSUPPORTED", re.I)

CLOUD = {
    "aws": re.compile(r"\b(aws|amazon|ec2|ecs|eks|fargate|lambda|elastic beanstalk|lightsail|app runner|amplify|dynamodb|aurora|rds|cognito|s3|cloudfront|sqs|sns|elasticache|opensearch service)\b", re.I),
    "azure": re.compile(r"\b(azure|app service|container apps|aks|cosmos db|azure sql)\b", re.I),
    "gcp": re.compile(r"\b(gcp|google cloud|cloud run|gke|cloud sql|firestore|bigquery|app engine|compute engine|cloud functions|spanner|alloydb)\b", re.I),
}
SAAS_NAME = re.compile(
    r"\b(vercel|netlify|firebase|supabase|planetscale|neon|cloudflare|aws|amazon|azure|google|gcp|heroku|"
    r"render|railway|fly\.io|digitalocean|auth0|clerk|okta|stripe|razorpay|twilio|sendgrid|algolia|pusher|"
    r"ably|sentry|datadog|new relic|github actions|cloud)\b", re.I)
VM_FORBIDDEN_HOST = re.compile(
    r"(vercel|netlify|firebase hosting|heroku|render|railway|fly\.io|cloudflare pages|amplify|app engine|"
    r"app runner|lambda|cloud functions|azure functions|static web apps|app service|container apps|cloud run)", re.I)
K8S = re.compile(r"(kubernetes|\bk8s\b|\beks\b|\baks\b|\bgke\b|openshift|\bk3s\b)", re.I)
BAD_PAYMENT = re.compile(r"(custom|in-house|self-built|own gateway|diy)", re.I)
GENERIC = ["best in class", "industry standard", "robust and scalable", "world-class", "cutting-edge"]


def load_kb():
    kb = {}
    d = ROOT / "data" / "kb"
    for f in sorted(d.glob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            kb.setdefault(e.get("layer"), {})[str(e.get("name", "")).lower()] = e
    return kb


def get(inp, path, default=None):
    cur = inp
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def eff(inp):
    """Effective input with documented defaults applied (valid inputs only)."""
    d = lambda p, x: get(inp, p, x)
    return {
        "type": d("project.type", "other"), "platforms": d("project.platforms", []) or [],
        "u_launch": d("scale.users_at_launch", 0) or 0, "u12": d("scale.users_12_months", 0) or 0,
        "peak": d("scale.peak_concurrent_users", None), "workload": d("scale.workload", "balanced"),
        "team": d("team.size", 1), "exp": d("team.experience", "intermediate"),
        "langs": [str(x).lower() for x in (d("team.languages", []) or [])],
        "devops": bool(d("team.has_devops", False)), "budget": d("budget.monthly_infra_usd", 0) or 0,
        "weeks": d("timeline.mvp_weeks", 12), "cloud": d("infrastructure.cloud_preference", "any"),
        "deploy": d("infrastructure.deployment_model", "managed_cloud"),
        "res": d("infrastructure.data_residency", "none"),
        "existing": d("infrastructure.existing_systems", []) or [],
        "rt": bool(d("requirements.realtime", False)), "offline": bool(d("requirements.offline_support", False)),
        "fts": bool(d("requirements.full_text_search", False)), "files": bool(d("requirements.file_media_storage", False)),
        "pay": bool(d("requirements.payments", False)), "auth": d("requirements.auth", "none"),
        "mt": bool(d("requirements.multi_tenant", False)), "ml": d("requirements.ml_features", "none"),
        "seo": bool(d("requirements.seo_critical", False)), "avail": str(d("requirements.availability", "99.9")),
        "p95": d("requirements.p95_latency_ms", None), "comp": [str(c).lower() for c in (d("compliance", []) or [])],
    }


def components(out):
    st = out.get("stack") or {}
    for layer in CORE:
        c = st.get(layer)
        if isinstance(c, dict):
            yield layer, layer, c
    for c in st.get("supporting") or []:
        if isinstance(c, dict):
            yield "supporting", str(c.get("layer")), c


def has_warning(out, fields_any=(), code_re=None, min_sev="warning"):
    order = {"info": 0, "warning": 1, "critical": 2}
    for w in out.get("warnings") or []:
        if order.get(w.get("severity"), -1) < order[min_sev]:
            continue
        if code_re and not code_re.search(str(w.get("code", ""))):
            continue
        if fields_any and not any(any(str(f).startswith(x) for x in fields_any) for f in (w.get("fields") or [])):
            continue
        return True
    return False


def assumption_mentions(out, *words):
    text = " ".join(str(a) for a in out.get("assumptions") or []).lower()
    return all(w in text for w in words)


def violations(inp, out, kb=None):
    kb = kb or load_kb()
    e = eff(inp)
    v = []
    status = out.get("status")
    warns = out.get("warnings") or []
    sev = [w.get("severity") for w in warns]
    if status == "ok" and any(s in ("warning", "critical") for s in sev):
        v.append("status 'ok' but warnings of severity warning/critical exist")
    if status == "ok_with_warnings" and not warns:
        v.append("status ok_with_warnings but no warnings")
    if status == "infeasible" and "critical" not in sev:
        v.append("status infeasible without any critical warning")
    if status in ("ok", "ok_with_warnings", "infeasible") and out.get("validation_errors"):
        v.append("valid input but validation_errors non-empty")
    if status not in ("ok", "ok_with_warnings", "infeasible", "invalid_input"):
        v.append(f"bad status {status!r}")
        return v
    # ---- expected warnings for contradictions (input-only rules) ----
    def need(desc, ok):
        if not ok:
            v.append("missing expected warning: " + desc)
    not_ok = status != "ok"
    if e["avail"] == "99.99" and (e["team"] <= 2 or e["exp"] == "beginner" or not e["devops"]):
        need("99.99 availability vs small/no-devops team", not_ok and has_warning(out, ["requirements.availability"]))
    if e["u12"] >= 1_000_000 and e["budget"] < 500:
        need("million-user scale vs tiny budget", not_ok and has_warning(out, ["budget", "scale"]))
    if e["weeks"] is not None and e["weeks"] <= 3 and len(e["platforms"]) >= 3:
        need("very short timeline vs many platforms", has_warning(out, ["timeline", "project.platforms"]))
    if "rbi_localisation" in e["comp"] and e["res"] != "india":
        need("rbi_localisation without india residency",
             has_warning(out, ["compliance", "infrastructure.data_residency"], min_sev="warning")
             or assumption_mentions(out, "rbi", "india"))
    if e["deploy"] == "air_gapped" and e["pay"]:
        need("air-gapped with payments", not_ok and has_warning(out, ["requirements.payments", "infrastructure.deployment_model"]))
    if e["cloud"] == "none" and e["deploy"] == "managed_cloud":
        need("cloud_preference none with managed_cloud",
             has_warning(out, ["infrastructure"]) or assumption_mentions(out, "cloud_preference"))
    if e["peak"] is not None and e["u12"] and e["peak"] > e["u12"]:
        need("peak concurrent users above 12-month users", has_warning(out, ["scale.peak_concurrent_users"], min_sev="info"))
    if e["u_launch"] > e["u12"] > 0 or (e["u12"] == 0 and e["u_launch"] > 0):
        need("launch users above 12-month users", has_warning(out, ["scale.users"], min_sev="info"))
    for s in e["existing"]:
        if any(re.search(p, str(s).lower()) for p in DEPRECATED):
            need(f"end-of-life existing system {s!r}",
                 any(EOL_WARNING_CODE.search(str(w.get("code", ""))) and
                     any(str(f).startswith("infrastructure.existing_systems") for f in (w.get("fields") or []))
                     for w in warns))
    if status == "invalid_input":
        if out.get("stack") is not None:
            v.append("invalid_input must have stack null")
        if not out.get("validation_errors"):
            v.append("invalid_input without validation_errors")
        return v
    st = out.get("stack")
    if st is None:
        if status != "infeasible":
            v.append("stack is null for a valid, feasible input")
        return v
    # ---- component-level rules ----
    comps = list(components(out))
    for group, layer, c in comps:
        choice = str(c.get("choice", ""))
        low = choice.lower()
        if low == "none":
            if group == "supporting":
                v.append(f"supporting layer {layer}: choice 'None' is not allowed")
            continue
        entry = kb.get(layer, {}).get(low)
        if entry is None:
            v.append(f"{layer}: choice {choice!r} is not an entry in the knowledge base")
        for p in DEPRECATED:
            if re.search(p, low):
                v.append(f"{layer}: deprecated/EOL choice {choice!r}")
        if entry is not None and str(entry.get("lifecycle_status", "")).lower() != "active":
            v.append(f"{layer}: KB lifecycle_status of {choice!r} is not active")
        for name, rx in CLOUD.items():
            if e["cloud"] in CLOUD and name != e["cloud"] and rx.search(choice):
                v.append(f"{layer}: {choice!r} belongs to {name} but cloud_preference={e['cloud']}")
            if e["cloud"] == "none" and rx.search(choice):
                v.append(f"{layer}: {choice!r} is a hyperscaler service but cloud_preference=none")
        if e["deploy"] in ("on_premise", "air_gapped"):
            if SAAS_NAME.search(choice) and "self-host" not in low:
                v.append(f"{layer}: SaaS/cloud choice {choice!r} under deployment_model={e['deploy']}")
            if entry is not None and (entry.get("saas_only") or entry.get("self_hostable") is False):
                v.append(f"{layer}: KB says {choice!r} is not self-hostable (deployment_model={e['deploy']})")
            if layer == "cdn":
                v.append(f"cdn recommended under deployment_model={e['deploy']}")
        if e["deploy"] == "self_hosted_cloud_vm" and layer == "hosting" and VM_FORBIDDEN_HOST.search(choice):
            v.append(f"hosting: managed PaaS/serverless {choice!r} under self_hosted_cloud_vm")
        if e["res"] not in ("none", None) and entry is not None and layer in ("hosting", "database", "storage", "cdn"):
            regions = [str(r).lower() for r in entry.get("regions", [])]
            if e["res"] not in regions and "global" not in regions and not entry.get("self_hostable"):
                v.append(f"{layer}: KB regions {regions} of {choice!r} do not cover residency {e['res']!r}")
        if K8S.search(choice) and not (e["devops"] and e["team"] >= 4):
            v.append(f"{layer}: Kubernetes-class choice {choice!r} without devops and team>=4")
        if layer == "payments" and BAD_PAYMENT.search(choice):
            v.append(f"payments: self-built card handling {choice!r}")
        if entry is not None and layer == "backend" and e["langs"]:
            langs = [str(x).lower() for x in entry.get("languages", [])]
            real = [x for x in e["langs"] if x not in ("sql", "html", "css")]
            if langs and real and not set(langs) & set(real):
                if not has_warning(out, ["team.languages"], re.compile(r"SKILL", re.I)):
                    v.append(f"backend {choice!r} ({langs}) mismatches team.languages without a SKILL warning")
    if str(out.get("architecture_style")) == "microservices" and not (e["team"] >= 8 and e["devops"]):
        v.append("microservices without team>=8 and devops")
    if e["pay"] and e["deploy"] != "air_gapped":
        if not any(layer == "payments" for _, layer, _ in comps):
            v.append("payments required but no supporting payments component")
    provided = set()
    for _, layer, c in comps:
        ent = kb.get(layer, {}).get(str(c.get("choice", "")).lower())
        if ent:
            provided.update(ent.get("provides", []))
    present = {layer for g, layer, _ in comps if g == "supporting"} | provided
    reqs = []
    if e["rt"]: reqs.append(("realtime", "realtime"))
    if e["fts"]: reqs.append(("search", "full_text_search"))
    if e["files"]: reqs.append(("storage", "file_media_storage"))
    if e["auth"] != "none": reqs.append(("auth", "auth"))
    if e["ml"] != "none": reqs.append(("ml", "ml_features"))
    for layer, why in reqs:
        if layer not in present and not (layer == "search" and kb.get("database", {}).get(
                str(st["database"].get("choice", "")).lower(), {}).get("fts")):
            v.append(f"requirement {why} but no supporting {layer} component (or KB 'provides')")
    # ---- over-engineering / static ----
    static_like = (e["type"] == "content_site" and not (e["rt"] or e["pay"] or e["auth"] != "none" or e["ml"] != "none" or e["files"]))
    if static_like and str(out.get("architecture_style")) in ("microservices", "service_oriented"):
        v.append("static-like content site with service architecture (over-engineering)")
    # ---- cost vs budget ----
    cost = out.get("estimated_monthly_cost_usd") or {}
    cmin, cmax = cost.get("min"), cost.get("max")
    if not isinstance(cmin, (int, float)) or not isinstance(cmax, (int, float)) or cmin < 0 or cmax < cmin:
        v.append(f"bad cost band {cost!r}")
    else:
        if cmin > e["budget"] * 1.25 + 5 and not (status != "ok" and has_warning(out, ["budget"])):
            v.append(f"cost.min {cmin} exceeds budget {e['budget']} without a budget warning")
        if status == "ok" and cmax > e["budget"] * 3 + 25:
            v.append(f"status ok but cost.max {cmax} >> budget {e['budget']}")
    # ---- compliance / integration notes ----
    notes = " ".join(str(x) for x in out.get("compliance_notes") or []).lower()
    for c in e["comp"]:
        if c.split("_")[0] not in notes:
            v.append(f"compliance_notes does not mention {c}")
    if e["res"] not in ("none", None) and e["res"] not in notes:
        v.append(f"compliance_notes does not mention residency {e['res']}")
    if "hipaa" in e["comp"] and "baa" not in notes:
        v.append("hipaa without BAA note")
    blob = json.dumps({"s": st, "w": warns, "i": out.get("integration_notes")}).lower()
    for s in e["existing"]:
        key = re.sub(r"\(.*?\)", "", str(s)).strip().lower().split(" ")[0:2]
        if " ".join(key) not in blob and key[0] not in blob:
            v.append(f"existing system {s!r} is not integrated/mentioned in stack, warnings or integration_notes")
    # ---- every active requirement must drive a decision ----
    drivers = set()
    for _, _, c in comps:
        drivers.update(str(x) for x in c.get("driven_by", []) or [])
    def driven(path):
        return any(d == path or d.startswith(path) for d in drivers)
    must = ["budget.monthly_infra_usd", "scale.users_12_months", "team.experience"]
    if e["langs"]: must.append("team.languages")
    if len(e["platforms"]) >= 2: must.append("project.platforms")
    if e["cloud"] != "any": must.append("infrastructure.cloud_preference")
    if e["deploy"] != "managed_cloud": must.append("infrastructure.deployment_model")
    if e["res"] not in ("none", None): must.append("infrastructure.data_residency")
    if e["comp"]: must.append("compliance")
    if e["seo"]: must.append("requirements.seo_critical")
    if e["mt"]: must.append("requirements.multi_tenant")
    if e["offline"]: must.append("requirements.offline_support")
    if e["p95"]: must.append("requirements.p95_latency_ms")
    for _, why in reqs: must.append("requirements." + why)
    if e["pay"]: must.append("requirements.payments")
    for path in must:
        if not driven(path):
            v.append(f"input {path} is active but no component lists it in driven_by")
    return v
