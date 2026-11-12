#!/usr/bin/env python3
"""StackSense strict validation gate. Stdlib only. Exit code 0 ONLY if every check passes.

Usage:  python gate/run_gate.py [--quick] [--json] [--only NAME] [--fuzz N]
The build agent MUST NOT edit anything under gate/ (see CLAUDE.md).
"""
import argparse, copy, json, os, random, re, socket, subprocess, sys, tempfile, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "gate"
sys.path.insert(0, str(GATE))
import oracle  # noqa: E402

CORE = oracle.CORE
PUBLIC = json.loads((ROOT / "data/scenarios/public_scenarios.json").read_text(encoding="utf-8"))


class Fail(Exception):
    pass


def set_path(d, path, val):
    cur = d
    parts = path.split(".")
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = val
    return d


def del_path(d, path):
    cur = d
    parts = path.split(".")
    for p in parts[:-1]:
        cur = cur.get(p, {})
    cur.pop(parts[-1], None)


def run_engine(scn, env=None, nonet=False, timeout=60):
    with tempfile.TemporaryDirectory() as td:
        inp, out = Path(td) / "in.json", Path(td) / "out.json"
        inp.write_text(scn if isinstance(scn, str) else json.dumps(scn), encoding="utf-8")
        e = dict(os.environ)
        e.update(env or {})
        pp = [str(ROOT)] + ([] if not nonet else [])
        if nonet:
            pp.insert(0, str(GATE / "nonet"))
        e["PYTHONPATH"] = os.pathsep.join(pp)
        t = time.time()
        p = subprocess.run([sys.executable, "-m", "stacksense", "run", str(inp), "--out", str(out)],
                           cwd=ROOT, env=e, capture_output=True, text=True, timeout=timeout)
        dt = time.time() - t
        if "Traceback" in (p.stderr or ""):
            raise Fail("traceback on stderr: " + p.stderr[-500:])
        if p.returncode != 0:
            raise Fail(f"engine exit code {p.returncode}: {(p.stderr or p.stdout)[-500:]}")
        if not out.exists():
            raise Fail("engine wrote no output file")
        raw = out.read_bytes()
        return json.loads(raw), raw, dt


def run_many(scns, **kw):
    def one(s):
        try:
            return run_engine(s, **kw)
        except Exception as ex:  # noqa
            return ex
    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(one, scns))


def key_view(out):
    return json.dumps({k: out.get(k) for k in ("status", "architecture_style", "stack", "estimated_monthly_cost_usd", "warnings")}, sort_keys=True)


def stack_view(out):
    st = out.get("stack") or {}
    sup = sorted((c.get("layer"), c.get("choice")) for c in st.get("supporting") or [])
    return (out.get("status"), out.get("architecture_style"), tuple(str((st.get(l) or {}).get("choice")) for l in CORE), tuple(sup))


# ----------------------------------------------------------------- generators
def gen_scenarios(n, seed):
    r = random.Random(seed)
    types = ["content_site", "web_app", "saas_b2b", "ecommerce", "marketplace", "social", "realtime_collab", "fintech",
             "healthtech", "data_analytics", "iot", "ai_ml_product", "internal_tool", "gaming", "api_platform", "other"]
    langs = ["python", "javascript", "typescript", "java", "csharp", "php", "go", "kotlin", "ruby", "rust", "sql"]
    out = []
    for i in range(n):
        u12 = r.choice([50, 500, 3000, 20000, 100000, 1_000_000, 8_000_000])
        ul = int(u12 * r.choice([0.01, 0.05, 0.2, 0.5]))
        budget = r.choice([0, 20, 100, 300, 1000, 5000, 25000])
        comp = r.sample(["gdpr", "dpdp", "hipaa", "pci_dss", "rbi_localisation", "soc2", "iso27001"], r.choice([0, 0, 1, 2]))
        s = {
            "scenario_id": f"F{i}",
            "project": {"name": f"Fuzz{i}", "type": r.choice(types), "description": "fuzz",
                        "platforms": r.sample(["web", "android", "ios", "desktop", "api_only"], r.choice([1, 1, 2, 3]))},
            "scale": {"traffic_pattern": r.choice(["steady", "spiky", "seasonal"]),
                      "workload": r.choice(["read_heavy", "balanced", "write_heavy"]),
                      "users_at_launch": ul, "users_12_months": u12,
                      "peak_concurrent_users": max(1, int(u12 * r.choice([0.01, 0.05, 0.1]))),
                      "data_volume_gb_12_months": r.choice([1, 20, 200, 2000])},
            "team": {"size": r.choice([1, 2, 3, 5, 8, 15]), "experience": r.choice(["beginner", "intermediate", "senior", "mixed"]),
                     "languages": r.sample(langs, r.choice([0, 1, 2, 3])), "has_devops": r.random() < 0.4},
            "budget": {"monthly_infra_usd": budget},
            "timeline": {"mvp_weeks": r.choice([2, 4, 8, 12, 24, 40])},
            "infrastructure": {"cloud_preference": r.choice(["any"] * 4 + ["aws", "gcp", "azure", "none"]),
                               "deployment_model": r.choice(["managed_cloud"] * 6 + ["self_hosted_cloud_vm", "on_premise", "air_gapped"]),
                               "data_residency": r.choice(["none"] * 3 + ["india", "eu", "us", "other"]),
                               "existing_systems": r.choice([[], [], [], ["PostgreSQL 14"], ["Python 2.7 monolith"], ["Okta SSO", "Salesforce"]])},
            "requirements": {"realtime": r.random() < 0.25, "offline_support": r.random() < 0.15, "full_text_search": r.random() < 0.3,
                             "file_media_storage": r.random() < 0.4, "payments": r.random() < 0.3,
                             "auth": r.choice(["none", "email_password", "social", "phone_otp", "enterprise_sso"]),
                             "multi_tenant": r.random() < 0.25, "ml_features": r.choice(["none"] * 3 + ["inference_api", "llm_rag", "training"]),
                             "seo_critical": r.random() < 0.3, "availability": r.choice(["99", "99.9", "99.95", "99.99"]),
                             "p95_latency_ms": r.choice([None, 100, 300, 1000])},
            "compliance": comp,
            "priorities": {k: r.randint(1, 5) for k in oracle.PRIORITY_KEYS},
        }
        out.append(s)
    return out


def base():
    return copy.deepcopy(PUBLIC[1])


def contradiction_cases():
    cs = []
    def case(name, mods, status_in=None):
        s = base()
        s["scenario_id"] = name
        for k, val in mods.items():
            set_path(s, k, val)
        cs.append((name, s, status_in))
    case("huge_scale_zero_budget", {"scale.users_12_months": 5_000_000, "scale.users_at_launch": 100_000,
                                    "scale.peak_concurrent_users": 200_000, "budget.monthly_infra_usd": 0},
         {"infeasible", "ok_with_warnings"})
    case("enterprise_avail_beginner_solo", {"requirements.availability": "99.99", "team.size": 1,
                                            "team.experience": "beginner", "team.has_devops": False},
         {"infeasible", "ok_with_warnings"})
    case("short_timeline_many_platforms", {"timeline.mvp_weeks": 2, "project.platforms": ["web", "android", "ios", "desktop"]},
         {"infeasible", "ok_with_warnings"})
    case("airgapped_payments", {"infrastructure.deployment_model": "air_gapped", "requirements.payments": True},
         {"infeasible", "ok_with_warnings"})
    case("onprem_internal", {"project.type": "internal_tool", "infrastructure.deployment_model": "on_premise",
                             "requirements.payments": False, "requirements.realtime": False}, None)
    case("rbi_not_india", {"compliance": ["rbi_localisation"], "infrastructure.data_residency": "none"}, None)
    case("hipaa_tiny_budget", {"compliance": ["hipaa"], "budget.monthly_infra_usd": 0, "project.type": "healthtech"}, None)
    case("peak_gt_users", {"scale.peak_concurrent_users": 999999}, None)
    case("launch_gt_12m", {"scale.users_at_launch": 90000, "scale.users_12_months": 100}, None)
    case("eol_existing", {"infrastructure.existing_systems": ["Python 2.7 monolith", "SQL Server 2014", "AngularJS 1.x frontend"]}, None)
    case("skill_mismatch", {"team.languages": ["php"], "requirements.ml_features": "training"}, None)
    case("static_but_huge_traffic", {"project.type": "content_site", "scale.users_12_months": 5_000_000, "scale.workload": "read_heavy",
                                     "requirements.realtime": False, "requirements.payments": False, "requirements.auth": "none",
                                     "requirements.file_media_storage": False, "requirements.full_text_search": False,
                                     "budget.monthly_infra_usd": 500, "team.size": 1, "team.has_devops": False}, None)
    case("tiny_internal_tool", {"project.type": "internal_tool", "team.size": 1, "scale.users_12_months": 40,
                                "scale.users_at_launch": 40, "scale.peak_concurrent_users": 10, "budget.monthly_infra_usd": 30,
                                "requirements.realtime": False, "requirements.payments": False}, None)
    case("cloud_none_managed", {"infrastructure.cloud_preference": "none", "infrastructure.deployment_model": "managed_cloud"}, None)
    for c in ("aws", "azure", "gcp"):
        case("cloud_pref_" + c, {"infrastructure.cloud_preference": c, "infrastructure.data_residency": "none"}, None)
    case("self_hosted_vm", {"infrastructure.deployment_model": "self_hosted_cloud_vm"}, None)
    return cs


INVALID = [
    ("empty_object", {}, ["project.type", "project.platforms", "scale.users_at_launch", "scale.users_12_months", "team.size",
                          "team.experience", "team.languages", "budget.monthly_infra_usd", "timeline.mvp_weeks"]),
    ("not_json", "{nope", []),
    ("top_level_list", "[]", []),
    ("bad_enum_type", ("project.type", "spaceship"), ["project.type"]),
    ("negative_users", ("scale.users_at_launch", -5), ["scale.users_at_launch"]),
    ("string_team_size", ("team.size", "three"), ["team.size"]),
    ("empty_platforms", ("project.platforms", []), ["project.platforms"]),
    ("unknown_platform", ("project.platforms", ["web", "toaster"]), ["project.platforms"]),
    ("priority_too_high", ("priorities.cost", 9), ["priorities.cost"]),
    ("priority_zero", ("priorities.security", 0), ["priorities.security"]),
    ("bad_availability", ("requirements.availability", "100"), ["requirements.availability"]),
    ("bad_compliance", ("compliance", ["sox"]), ["compliance"]),
    ("bool_as_int", ("team.size", True), ["team.size"]),
    ("float_team", ("team.size", 2.5), ["team.size"]),
    ("zero_weeks", ("timeline.mvp_weeks", 0), ["timeline.mvp_weeks"]),
    ("languages_not_list", ("team.languages", "python"), ["team.languages"]),
    ("negative_budget", ("budget.monthly_infra_usd", -1), ["budget.monthly_infra_usd"]),
    ("p95_zero", ("requirements.p95_latency_ms", 0), ["requirements.p95_latency_ms"]),
    ("bad_deploy_model", ("infrastructure.deployment_model", "cloudy"), ["infrastructure.deployment_model"]),
    ("null_team_section", ("team", None), ["team"]),
    ("multi_error", [("project.type", "x"), ("team.size", -1), ("budget.monthly_infra_usd", "abc")],
     ["project.type", "team.size", "budget.monthly_infra_usd"]),
]

EXTRAS = {  # extra.* parameters the engine must support, with a low/high test pair
    "extra.expected_rps": (5, 5000),
    "extra.geo_distribution": ("single_region", "global"),
    "extra.vendor_lock_in_tolerance": ("low", "high"),
    "extra.existing_licences": ([], ["Microsoft 365 E5", "Oracle Database Enterprise"]),
    "extra.hiring_plan_6m": (0, 10),
    "extra.data_sensitivity": ("public", "restricted"),
    "extra.integration_needs": ([], ["erp", "crm", "payments_gateway", "sms"]),
    "extra.sync_conflict_tolerance": ("last_write_wins", "strict_consistency"),
}

CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


# ----------------------------------------------------------------- output schema
def schema_errors(out, inp):
    e = []
    for k in ("status", "summary", "architecture_style", "stack", "estimated_monthly_cost_usd", "warnings", "assumptions", "validation_errors"):
        if k not in out:
            e.append(f"missing top-level {k}")
    if e:
        return e
    if out["status"] == "invalid_input":
        return []
    if out["architecture_style"] not in ("static", "monolith", "modular_monolith", "serverless", "service_oriented", "microservices", "hybrid", "other"):
        e.append("bad architecture_style")
    if not isinstance(out["summary"], str) or len(out["summary"]) < 30:
        e.append("summary too short")
    st = out["stack"]
    if st is None:
        return e
    allowed_sup = {"cache", "queue", "search", "auth", "storage", "cdn", "realtime", "payments", "ml", "ci_cd", "observability", "other"}
    for layer in CORE:
        c = st.get(layer)
        if not isinstance(c, dict):
            e.append(f"stack.{layer} missing")
            continue
        if not c.get("alternatives"):
            e.append(f"{layer}: needs >=1 alternative")
        if not c.get("what_would_change"):
            e.append(f"{layer}: missing what_would_change counterfactuals")
    for group, layer, c in oracle.components(out):
        for k in ("choice", "justification", "driven_by", "alternatives"):
            if k not in c:
                e.append(f"{layer}: missing {k}")
        if group == "supporting" and layer not in allowed_sup:
            e.append(f"unknown supporting layer {layer!r}")
        for p in c.get("driven_by", []) or []:
            if not (p in oracle.STD_PATHS or str(p).startswith("extra.")):
                e.append(f"{layer}: driven_by path {p!r} is not an input field")
        for a in c.get("alternatives", []) or []:
            if not (isinstance(a, dict) and a.get("choice") and len(str(a.get("why_not", ""))) >= 25):
                e.append(f"{layer}: alternative needs choice and why_not>=25 chars")
        j = str(c.get("justification", ""))
        if len(j) < 60:
            e.append(f"{layer}: justification shorter than 60 chars")
        if any(g in j.lower() for g in oracle.GENERIC) and not re.search(r"\d", j):
            e.append(f"{layer}: generic marketing wording without specifics")
        hit = False
        for p in c.get("driven_by", []) or []:
            val = oracle.get(inp, p)
            toks = [str(p).split(".")[-1].replace("_", " ").lower()]
            if val is not None and not isinstance(val, (dict, list)):
                toks.append(str(val).lower())
            if isinstance(val, list):
                toks += [str(x).lower() for x in val]
            if any(t and t in j.lower() for t in toks):
                hit = True
        if c.get("driven_by") and not hit:
            e.append(f"{layer}: justification never references the values of its driven_by inputs")
    cost = out["estimated_monthly_cost_usd"]
    if not (isinstance(cost, dict) and "min" in cost and "max" in cost and cost.get("assumptions")):
        e.append("estimated_monthly_cost_usd needs min, max, assumptions")
    for w in out["warnings"]:
        if not (isinstance(w, dict) and w.get("code") and w.get("severity") in ("info", "warning", "critical") and w.get("message")):
            e.append(f"bad warning object {w!r}")
    return e


def full_problems(scn, out, kb):
    return [f"[schema] {x}" for x in schema_errors(out, scn)] + [f"[oracle] {x}" for x in oracle.violations(scn, out, kb)]


# ----------------------------------------------------------------- checks
@check
def structure():
    p = []
    for f in ["README.md", "PROGRESS.md", "docs/KB_AUDIT.md", "stacksense/__main__.py", ".env.example"]:
        if not (ROOT / f).exists():
            p.append(f"missing {f}")
    n = sum(len(re.findall(r"\bdef test_", f.read_text(encoding="utf-8", errors="ignore"))) for f in (ROOT / "tests").glob("test*.py")) if (ROOT / "tests").exists() else 0
    if n < 60:
        p.append(f"only {n} unit tests (need >= 60)")
    return p


@check
def knowledge_base():
    p = []
    kb = oracle.load_kb()
    for layer in CORE:
        if len(kb.get(layer, {})) < 8:
            p.append(f"KB layer {layer}: {len(kb.get(layer, {}))} entries (need >= 8)")
    sup = sum(len(v) for k, v in kb.items() if k not in CORE)
    if sup < 25:
        p.append(f"KB supporting entries: {sup} (need >= 25)")
    for layer in ("cache", "queue", "search", "auth", "storage", "cdn", "realtime", "payments", "ml", "ci_cd", "observability"):
        if len(kb.get(layer, {})) < 2:
            p.append(f"KB supporting layer {layer} has < 2 entries")
    names = set()
    for layer, ents in kb.items():
        for key, en in ents.items():
            tag = f"{layer}/{en.get('name')}"
            for f in ("name", "layer", "lifecycle_status", "languages", "regions", "self_hostable", "saas_only", "cloud",
                      "cost_model", "strengths", "limits", "ops_burden", "maturity", "provides", "sources"):
                if f not in en:
                    p.append(f"{tag}: missing KB field {f}")
            if str(en.get("lifecycle_status")).lower() != "active":
                p.append(f"{tag}: lifecycle_status must be 'active'")
            srcs = en.get("sources") or []
            if not srcs:
                p.append(f"{tag}: no sources")
            for s in srcs:
                if not (str(s.get("url", "")).startswith("https://") and re.fullmatch(r"2026-1[01]-\d\d", str(s.get("accessed", "")))):
                    p.append(f"{tag}: source needs https url and accessed date in Oct/Nov 2026")
            for pat in oracle.DEPRECATED:
                if re.search(pat, key):
                    p.append(f"{tag}: deprecated/EOL name in KB")
            if (layer, key) in names:
                p.append(f"duplicate KB entry {tag}")
            names.add((layer, key))
    audit = (ROOT / "docs/KB_AUDIT.md")
    txt = audit.read_text(encoding="utf-8").lower() if audit.exists() else ""
    for layer, ents in kb.items():
        for key, en in ents.items():
            if str(en.get("name", "")).lower() not in txt:
                p.append(f"docs/KB_AUDIT.md does not mention {en.get('name')}")
    return p[:60]


@check
def public_scenarios():
    kb, p = oracle.load_kb(), []
    res = run_many(PUBLIC)
    for s, r in zip(PUBLIC, res):
        if isinstance(r, Exception):
            p.append(f"{s['scenario_id']}: {r}")
            continue
        out, raw, dt = r
        p += [f"{s['scenario_id']}: {x}" for x in full_problems(s, out, kb)]
        if dt > 5:
            p.append(f"{s['scenario_id']}: took {dt:.1f}s (limit 5s)")
        if out.get("status") == "invalid_input":
            p.append(f"{s['scenario_id']}: valid public scenario rejected")
    return p[:80]


@check
def determinism_and_invariance():
    p = []
    for s in PUBLIC:
        a = run_engine(s, env={"PYTHONHASHSEED": "1"})[1]
        b = run_engine(s, env={"PYTHONHASHSEED": "777"})[1]
        if a != b:
            p.append(f"{s['scenario_id']}: output differs across runs / hash seeds (non-deterministic)")
        ref = json.loads(a)
        m = copy.deepcopy(s)
        m["scenario_id"], m["project"]["name"], m["project"]["description"] = "ZZ9", "Qwerty", "lorem ipsum dolor"
        for path in ("team.languages", "compliance", "project.platforms", "infrastructure.existing_systems"):
            v = oracle.get(m, path)
            if isinstance(v, list):
                set_path(m, path, list(reversed(v)))
        m = {k: m[k] for k in reversed(list(m.keys()))}
        o2 = run_engine(m)[0]
        if stack_view(ref) != stack_view(o2):
            p.append(f"{s['scenario_id']}: stack changes when only id/name/description/list order/key order change (hard-coding or description dependence)")
        if json.dumps(ref.get("estimated_monthly_cost_usd"), sort_keys=True) != json.dumps(o2.get("estimated_monthly_cost_usd"), sort_keys=True):
            p.append(f"{s['scenario_id']}: cost changes with irrelevant edits")
    return p


@check
def llm_off_and_offline():
    p = []
    for s in PUBLIC:
        ref = run_engine(s)[0]
        for env in ({"STACKSENSE_LLM": "off"}, {"STACKSENSE_LLM": "on"}):
            o = run_engine(s, env=env, nonet=True)[0]
            if stack_view(o) != stack_view(ref):
                p.append(f"{s['scenario_id']}: stack differs with {env} and network blocked")
    bad = re.compile(r"\b(openai|anthropic|ollama|litellm|google\.generativeai|google\.genai|cohere|mistralai|langchain|httpx|requests|urllib\.request|http\.client|socket)\b")
    for f in (ROOT / "stacksense").rglob("*.py"):
        t = f.read_text(encoding="utf-8", errors="ignore")
        if f.name != "llm_assist.py" and bad.search(t) and f.name != "server.py":
            p.append(f"{f.relative_to(ROOT)}: references an LLM/network library outside llm_assist.py/server.py")
        if f.name not in ("llm_assist.py", "cli.py", "__main__.py") and "llm_assist" in t:
            p.append(f"{f.relative_to(ROOT)}: decision code references llm_assist")
    return p


@check
def anti_hardcoding():
    p = []
    names = ["devfolio", "fixit now", "boardroom", "quickcredit", "peopledesk", "khetsurvey"]
    pat_ids = re.compile(r"""["']P[1-6]["']""")
    pat_cmp = re.compile(r"scenario_id[^\n]*(==|!=|\bin\b|\.startswith|\.get\([^)]*\)\s*\[)")
    for f in list((ROOT / "stacksense").rglob("*.py")) + list((ROOT / "data").rglob("*.json")):
        if "scenarios" in f.parts:
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        low = t.lower()
        if pat_ids.search(t):
            p.append(f"{f.relative_to(ROOT)}: references public scenario ids")
        if pat_cmp.search(t):
            p.append(f"{f.relative_to(ROOT)}: logic keyed on scenario_id")
        for n in names:
            if n in low:
                p.append(f"{f.relative_to(ROOT)}: mentions public project name {n!r}")
        if re.search(r"(_output\.json|public_scenarios|outputs[/\\])", t):
            p.append(f"{f.relative_to(ROOT)}: reads canned outputs/scenario files")
    return p


@check
def invalid_inputs():
    p = []
    for name, spec, expect in INVALID:
        if isinstance(spec, str):
            scn = spec
        elif isinstance(spec, dict):
            scn = spec
        else:
            scn = copy.deepcopy(PUBLIC[1])
            for path, val in (spec if isinstance(spec, list) else [spec]):
                set_path(scn, path, val)
        try:
            out = run_engine(scn)[0]
        except Exception as ex:  # noqa
            p.append(f"{name}: {ex}")
            continue
        if out.get("status") != "invalid_input":
            p.append(f"{name}: status {out.get('status')!r}, expected invalid_input")
            continue
        if out.get("stack") is not None:
            p.append(f"{name}: stack must be null")
        errs = out.get("validation_errors") or []
        if not errs:
            p.append(f"{name}: no validation_errors")
        fields = [str(x.get("field")) for x in errs if isinstance(x, dict)]
        for ef in expect:
            if not any(f == ef or f.startswith(ef) for f in fields):
                p.append(f"{name}: no validation error for field {ef} (got {fields})")
        if any(not (isinstance(x, dict) and x.get("message")) for x in errs):
            p.append(f"{name}: validation error without message")
    return p


@check
def minimal_input_defaults():
    p = []
    kb = oracle.load_kb()
    scn = copy.deepcopy(PUBLIC[0])
    keep = {"project": ["type", "platforms"], "scale": ["users_at_launch", "users_12_months"],
            "team": ["size", "experience", "languages"], "budget": ["monthly_infra_usd"], "timeline": ["mvp_weeks"]}
    mini = {sec: {k: scn[sec][k] for k in ks} for sec, ks in keep.items()}
    out = run_engine(mini)[0]
    if out.get("status") not in ("ok", "ok_with_warnings"):
        return [f"minimal input gave status {out.get('status')}: {out.get('validation_errors')}"]
    text = json.dumps(out.get("assumptions")).lower()
    for path in sorted(oracle.STD_PATHS):
        if path in ("project.name", "project.description"):
            continue
        sec, key = (path.split(".") + [""])[:2] if "." in path else (path, "")
        if path.startswith("priorities."):
            continue
        if oracle.get(mini, path) is None and not (key == "" and path in mini):
            if key.lower() not in text and path.lower() not in text:
                p.append(f"default for omitted {path} not recorded in assumptions")
    if "priorit" not in text:
        p.append("default priorities not recorded in assumptions")
    p += [f"[minimal] {x}" for x in full_problems(mini, out, kb)]
    return p


@check
def contradictions_and_hard_constraints():
    p, kb = [], oracle.load_kb()
    cases = contradiction_cases()
    res = run_many([c[1] for c in cases])
    for (name, scn, status_in), r in zip(cases, res):
        if isinstance(r, Exception):
            p.append(f"{name}: {r}")
            continue
        out = r[0]
        if status_in and out.get("status") not in status_in:
            p.append(f"{name}: status {out.get('status')!r} not in {sorted(status_in)}")
        p += [f"{name}: {x}" for x in full_problems(scn, out, kb)]
    return p[:80]


@check
def extras_change_outputs():
    p, changed = [], {}
    for key, (lo, hi) in EXTRAS.items():
        diffs = 0
        for s in PUBLIC:
            a, b = copy.deepcopy(s), copy.deepcopy(s)
            set_path(a, key, lo)
            set_path(b, key, hi)
            try:
                oa, ob = run_engine(a)[0], run_engine(b)[0]
            except Exception as ex:  # noqa
                p.append(f"{key}: engine failed: {ex}")
                break
            if key_view(oa) != key_view(ob) or oa.get("assumptions") != ob.get("assumptions"):
                diffs += 1
        changed[key] = diffs
    if sum(1 for v in changed.values() if v >= 1) < 7:
        p.append(f"extras must visibly affect output in >= 7 of {len(EXTRAS)} cases; effects: {changed}")
    for key, d in changed.items():
        if d == 0:
            p.append(f"extra parameter {key} never changes any output (unjustified input)")
    return p


@check
def fuzz_and_diversity(n=120):
    p, kb = [], oracle.load_kb()
    scns = gen_scenarios(n, 20261112)
    res = run_many(scns)
    outs = []
    for s, r in zip(scns, res):
        if isinstance(r, Exception):
            p.append(f"{s['scenario_id']}: {r}")
            continue
        out = r[0]
        outs.append((s, out))
        p += [f"{s['scenario_id']}: {x}" for x in full_problems(s, out, kb)]
    if len(outs) < n * 0.95:
        p.append("too many engine failures in fuzz")
    pub = [o[0] for o in run_many(PUBLIC) if not isinstance(o, Exception)]
    allout = [o for _, o in outs] + pub
    tuples = {stack_view(o)[2] for o in allout if o.get("stack")}
    if len(tuples) < 25:
        p.append(f"only {len(tuples)} distinct core stacks across {len(allout)} scenarios (need >= 25)")
    for i, layer in enumerate(CORE):
        d = {stack_view(o)[2][i] for o in allout if o.get("stack")}
        if len(d) < 5:
            p.append(f"layer {layer}: only {len(d)} distinct choices overall (need >= 5)")
    ms = sum(1 for o in allout if o.get("architecture_style") == "microservices")
    if allout and ms / len(allout) > 0.05:
        p.append("microservices recommended too often (over-engineering)")
    infeas = sum(1 for o in allout if o.get("status") == "infeasible")
    if allout and infeas / len(allout) > 0.35:
        p.append("infeasible returned for > 35% of scenarios (engine gives up too easily)")
    fit = tot = 0
    for s, o in outs:
        be = (o.get("stack") or {}).get("backend") or {}
        ent = kb.get("backend", {}).get(str(be.get("choice", "")).lower())
        real = [x for x in oracle.eff(s)["langs"] if x not in ("sql", "html", "css")]
        if ent and real:
            tot += 1
            fit += bool(set(str(x).lower() for x in ent.get("languages", [])) & set(real))
    if tot >= 20 and fit / tot < 0.85:
        p.append(f"backend matches team language only {fit}/{tot} times (need >= 85%)")
    # justification must be scenario specific
    seen = {}
    for o in allout:
        for g, layer, c in oracle.components(o):
            seen.setdefault((layer, c.get("choice")), []).append(c.get("justification"))
    for k, js in seen.items():
        if len(js) >= 6 and len(set(js)) < max(2, len(js) // 3):
            p.append(f"justification for {k} is near-identical across {len(js)} scenarios (templated, not scenario-specific)")
    return p[:80]


@check
def local_sensitivity():
    p = []
    scns = gen_scenarios(30, 4242)
    perts = [("scale.users_12_months", lambda v: int(v * 1.2) + 1), ("budget.monthly_infra_usd", lambda v: v * 1.1 + 1),
             ("priorities.cost", lambda v: min(5, v + 1) if v < 5 else 4), ("scale.peak_concurrent_users", lambda v: int(v * 1.1) + 1)]
    mods = []
    for s in scns:
        for path, fn in perts:
            m = copy.deepcopy(s)
            set_path(m, path, fn(oracle.get(m, path)))
            mods.append(m)
    ra, rb = run_many(scns), run_many(mods)
    big = tot = 0
    for i, a in enumerate(ra):
        if isinstance(a, Exception):
            continue
        for j in range(len(perts)):
            b = rb[i * len(perts) + j]
            if isinstance(b, Exception):
                continue
            tot += 1
            ca, cb = stack_view(a[0])[2], stack_view(b[0])[2]
            if sum(x != y for x, y in zip(ca, cb)) >= 2:
                big += 1
    if tot and big / tot > 0.12:
        p.append(f"small input perturbations flip >= 2 core layers in {big}/{tot} cases (unstable engine)")
    return p


@check
def unit_tests():
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=ROOT, capture_output=True, text=True, timeout=900)
    return [] if r.returncode == 0 else ["unit tests failed: " + (r.stderr or r.stdout)[-600:]]


@check
def web_ui():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    proc = subprocess.Popen([sys.executable, "-m", "stacksense", "serve", "--port", str(port)], cwd=ROOT,
                            env={**os.environ, "PYTHONPATH": str(ROOT)}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p = []
    try:
        base_url = f"http://127.0.0.1:{port}"
        for _ in range(40):
            try:
                html = urllib.request.urlopen(base_url + "/", timeout=2).read().decode("utf-8", "ignore")
                break
            except Exception:  # noqa
                time.sleep(0.25)
        else:
            return ["serve: server did not start within 10s"]
        if "<html" not in html.lower():
            p.append("GET / did not return HTML")
        req = urllib.request.Request(base_url + "/api/recommend", data=json.dumps(PUBLIC[1]).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        api = json.loads(urllib.request.urlopen(req, timeout=15).read())
        cli = run_engine(PUBLIC[1])[0]
        if stack_view(api) != stack_view(cli):
            p.append("web API stack differs from CLI stack")
    except Exception as ex:  # noqa
        p.append(f"serve check failed: {ex}")
    finally:
        proc.terminate()
    return p


@check
def docs():
    p = []
    t = (ROOT / "README.md").read_text(encoding="utf-8", errors="ignore").lower() if (ROOT / "README.md").exists() else ""
    for w in ("architecture", "prerequisite", "setup", "scenario", "llm", "structure", "credits", "version"):
        if w not in t:
            p.append(f"README missing section about '{w}'")
    if "python -m stacksense run" not in t:
        p.append("README lacks the exact run command 'python -m stacksense run'")
    for f, minlen in (("docs/REPORT_NOTES.md", 6000), ("PROGRESS.md", 1500)):
        fp = ROOT / f
        if not fp.exists() or len(fp.read_text(encoding="utf-8", errors="ignore")) < minlen:
            p.append(f"{f} missing or too short (< {minlen} chars)")
    return p


@check
def gate_integrity():
    bl = GATE / "BASELINE"
    if not bl.exists():
        return ["gate/BASELINE missing"]
    sha = bl.read_text().strip()
    r = subprocess.run(["git", "diff", "--stat", sha, "--", "gate", "data/scenarios", "docs/SPEC.md", "CLAUDE.md", ":!gate/BASELINE"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return ["git diff against BASELINE failed: " + r.stderr[-200:]]
    return ["protected files modified since BASELINE:\n" + r.stdout] if r.stdout.strip() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--fuzz", type=int, default=None)
    a = ap.parse_args()
    results, ok = [], True
    for fn in CHECKS:
        if a.only and a.only not in fn.__name__:
            continue
        t = time.time()
        try:
            if fn is fuzz_and_diversity:
                probs = fn(a.fuzz or (25 if a.quick else 120))
            else:
                probs = fn()
        except Exception as ex:  # noqa
            probs = [f"check crashed: {type(ex).__name__}: {ex}"]
        results.append({"check": fn.__name__, "passed": not probs, "seconds": round(time.time() - t, 1), "problems": probs})
        ok &= not probs
    if a.json:
        print(json.dumps({"passed": ok, "results": results}, indent=1))
    else:
        for r in results:
            print(("PASS " if r["passed"] else "FAIL ") + f"{r['check']} ({r['seconds']}s)")
            for x in r["problems"][:25]:
                print("   -", x)
            if len(r["problems"]) > 25:
                print(f"   ... {len(r['problems']) - 25} more")
        print("\nGATE:", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
