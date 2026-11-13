"""StackSense decision engine: rules + weighted scoring over a curated knowledge base. Fully deterministic, no LLM, no network.

Pipeline: validate -> derive features -> hard-constraint filters -> joint scoring (hosting x backend x frontend x database x supporting)
-> warnings/conflicts -> cost band -> explanations -> output JSON.
"""
import math
import re

from . import kb as kbmod
from .validate import validate

ENGINE_VERSION = "1.0.0"
RK = {"cost": "cost", "time_to_market": "ttm", "scalability": "scale", "performance": "perf", "maintainability": "maint", "security": "sec"}
RN = {"ttm": "time to market", "cost": "cost efficiency", "scale": "scalability", "perf": "performance", "maint": "maintainability", "sec": "security"}
ATTEST = ("pci_dss", "hipaa", "soc2", "iso27001")
DYNAMIC_TYPES = {"web_app", "saas_b2b", "ecommerce", "marketplace", "social", "realtime_collab", "fintech", "healthtech", "data_analytics",
                 "iot", "ai_ml_product", "internal_tool", "gaming", "api_platform"}
K8S = re.compile(r"(kubernetes|\bk8s\b|\beks\b|\baks\b|\bgke\b|openshift|\bk3s\b)", re.I)


def fv(val):
    if val is True:
        return "true"
    if val is False:
        return "false"
    if isinstance(val, list):
        return "[" + ", ".join(str(x) for x in val) + "]" if val else "[]"
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)


class Feat:
    pass


def derive(n, A):
    f = Feat()
    s, t, i, r, x = n["scale"], n["team"], n["infrastructure"], n["requirements"], n["extra"]
    f.n, f.type = n, n["project"]["type"]
    f.platforms = [p for p in n["project"]["platforms"] if p != "api_only"]
    f.api_only = n["project"]["platforms"] == ["api_only"]
    f.u12, f.u0 = s["users_12_months"], s["users_at_launch"]
    f.peak = s["peak_concurrent_users"]
    if f.peak is None:
        f.peak = max(1, int(f.u12 * 0.1))
        A.append(f"scale.peak_concurrent_users estimated as 10% of scale.users_12_months = {f.peak}")
    f.traffic, f.workload, f.gb = s["traffic_pattern"], s["workload"], s["data_volume_gb_12_months"]
    f.team, f.exp, f.devops = t["size"], t["experience"], t["has_devops"]
    f.langs = t["languages"]
    f.real_langs = [l for l in f.langs if l not in ("sql", "html", "css")]
    f.budget, f.weeks = n["budget"]["monthly_infra_usd"], n["timeline"]["mvp_weeks"]
    f.cloud, f.deploy, f.res = i["cloud_preference"], i["deployment_model"], i["data_residency"]
    f.existing = i["existing_systems"]
    f.ex_low = " ".join(e.lower() for e in f.existing)
    f.rt, f.offline, f.fts, f.files = r["realtime"], r["offline_support"], r["full_text_search"], r["file_media_storage"]
    f.pay, f.auth, f.mt, f.ml, f.seo = r["payments"], r["auth"], r["multi_tenant"], r["ml_features"], r["seo_critical"]
    f.avail, f.p95 = r["availability"], r["p95_latency_ms"]
    f.comp = n["compliance"]
    f.att = [c for c in f.comp if c in ATTEST]
    f.prio = n["priorities"]
    f.x = x
    f.rps = x.get("expected_rps")
    f.hiring = x.get("hiring_plan_6m", 0)
    f.geo = x.get("geo_distribution", "single_region")
    f.lock = x.get("vendor_lock_in_tolerance", "medium")
    f.sens = x.get("data_sensitivity", "internal")
    f.licences = " ".join(x.get("existing_licences", []))
    f.integr = x.get("integration_needs", [])
    f.sync = x.get("sync_conflict_tolerance", "last_write_wins")
    for key, val in x.items():
        A.append(f"Extra parameter extra.{key} = {fv(val)} was applied (see component justifications)")
    for key, dflt in (("geo_distribution", "single_region"), ("vendor_lock_in_tolerance", "medium"), ("data_sensitivity", "internal"),
                      ("sync_conflict_tolerance", "last_write_wins")):
        if key not in x:
            A.append(f"Default applied: extra.{key} = {dflt}")
    f.tier = 0 if f.u12 <= 5000 else 1 if f.u12 <= 50000 else 2 if f.u12 <= 500000 else 3 if f.u12 <= 5_000_000 else 4
    if f.rps is not None:
        trps = 0 if f.rps <= 5 else 1 if f.rps <= 50 else 2 if f.rps <= 500 else 3 if f.rps <= 5000 else 4
        f.tier = max(f.tier, trps)
    team_eff = f.team + f.hiring
    f.team_eff = team_eff
    base = {"beginner": 1, "intermediate": 2, "mixed": 2, "senior": 3}[f.exp]
    f.ops_cap = min(5, base + (2 if f.devops else 0) + (1 if team_eff >= 5 else 0))
    p = dict(f.prio)
    if f.sens == "restricted":
        p["security"] = min(5, p["security"] + 2)
    elif f.sens == "confidential":
        p["security"] = min(5, p["security"] + 1)
    if f.p95 is not None and f.p95 <= 150:
        p["performance"] = min(5, p["performance"] + 1)
    tot = float(sum(p.values()))
    f.w = {RK[k]: v / tot for k, v in p.items()}
    f.pw = p
    f.rbi_res = "rbi_localisation" in f.comp
    f.eff_res = "india" if f.rbi_res else f.res
    f.dynamic = bool(f.auth != "none" or f.pay or f.rt or f.ml != "none" or f.files or f.mt or f.offline or f.fts or f.type in DYNAMIC_TYPES or f.type == "other" and f.u12 > 0 and False)
    f.needs_backend = f.dynamic
    f.static_like = not f.dynamic
    return f


# ------------------------------------------------------------------ constraints
def exclusion(e, layer, f, host=None):
    """Return the reason an entry is excluded by a HARD constraint, or None when allowed."""
    if layer in ("frontend", "backend"):
        return None  # frameworks are software, not hosted services: only the host decides regions/deployment
    c = e["cloud"]
    if f.cloud in ("aws", "azure", "gcp"):
        if layer == "hosting" and c != f.cloud:
            return f"cloud_preference={f.cloud} requires a {f.cloud} host"
        if c not in ("neutral", f.cloud):
            return f"belongs to {c} but cloud_preference={f.cloud}"
    if f.cloud == "none" and c != "neutral":
        return "cloud_preference=none excludes hyperscaler services"
    if f.deploy in ("on_premise", "air_gapped"):
        if not (layer == "payments" and f.deploy == "on_premise"):
            if not e["self_hostable"] or e["saas_only"]:
                return f"not self-hostable (deployment_model={f.deploy})"
        if layer == "cdn":
            return f"no CDN under deployment_model={f.deploy}"
    if layer == "hosting":
        ht = e["hosting_type"]
        if f.deploy in ("on_premise", "air_gapped") and ht != "onprem":
            return f"deployment_model={f.deploy} needs self-managed servers"
        if f.deploy == "self_hosted_cloud_vm" and ht != "vm":
            return "deployment_model=self_hosted_cloud_vm needs virtual machines"
        if f.deploy == "managed_cloud" and ht == "onprem" and f.cloud != "none":
            return "on-premises hosting does not match managed_cloud"
        if f.cloud == "none" and ht not in ("onprem", "vm"):
            return "cloud_preference=none excludes managed platforms"
    if f.deploy == "self_hosted_cloud_vm" and layer == "database" and not e["self_hostable"]:
        return "managed database does not match self_hosted_cloud_vm"
    if layer == "payments":
        if f.eff_res == "india" and "india" not in e["regions"]:
            return "payment processing must stay in India (RBI/DPDP data residency)"
    elif f.eff_res != "none" and not e["self_hostable"]:
        if f.eff_res not in e["regions"] and "global" not in e["regions"]:
            return f"no verified {f.eff_res} region (data_residency={f.eff_res})"
    if f.att and layer in ("hosting", "database", "storage", "ml") and not e["self_hostable"]:
        miss = [a for a in f.att if a not in e["compliance"]]
        if miss:
            return f"vendor attestation for {', '.join(miss)} is not recorded in the knowledge base"
    if K8S.search(e["name"]) and not (f.devops and f.team >= 4):
        return "Kubernetes-class platform needs has_devops=true and team.size>=4"
    if layer == "hosting":
        if f.rt and not e["websockets"]:
            return "no persistent websocket support (requirements.realtime=true)"
    return None


def cost_of(e, f):
    if e["layer"] == "database" and e["name"] in getattr(f, "reuse", ()):
        return 0.0, 0.0  # existing system: no new spend
    lf = 1.0
    if f.rps is not None and e["layer"] in ("hosting", "database", "cache"):
        lf += min(f.rps / 2000.0, 2.0)
    k = f.u12 / 1000.0
    cmin = e["cost"]["fixed"][0] + e["cost"]["per_1k_users"][0] * k * lf
    cmax = e["cost"]["fixed"][1] + e["cost"]["per_1k_users"][1] * k * lf
    if f.traffic == "spiky":
        cmax *= 1.25
    elif f.traffic == "seasonal":
        cmax *= 1.1
    return cmin, cmax


def base_score(e, f):
    return sum(f.w[k] * e["ratings"][k] for k in f.w)


def penalties(e, f):
    p = 0.0
    p += 0.45 * max(0, e["ops_burden"] - f.ops_cap)
    if f.weeks <= 6 and e["ops_burden"] >= 4:
        p += 0.3
    if f.u12 > e["scale_cap_users"]:
        p += min(3.0, 1.0 + math.log10(f.u12 / float(e["scale_cap_users"])))
    cmin, cmax = cost_of(e, f)
    mid = (cmin + cmax) / 2.0
    if f.budget <= 0:
        p += 2.0 if cmax > 0 else 0.0
    else:
        p += max(0.0, min(3.0, (mid / f.budget - 0.15) * 3.0)) * (0.4 + 0.12 * f.prio["cost"])
    if f.lock == "low" and (e["cloud"] != "neutral" or e["saas_only"]):
        p += 0.7
    elif f.lock == "high" and e["saas_only"]:
        p -= 0.2
    if f.sens in ("confidential", "restricted") and not e["self_hostable"] and not e["compliance"] and e["layer"] in ("hosting", "database", "storage"):
        p += 0.6
    return p


def skill(e, f, weight):
    if not f.real_langs:
        return 0.0
    el = [x.lower() for x in e["languages"]]
    if not el:
        return 0.3 * weight
    return (1.0 if set(el) & set(f.real_langs) else -1.0) * weight


def cloud_affinity(e, host):
    hc, ec = host["cloud"], e["cloud"]
    if ec == "neutral":
        return 0.0
    if hc == ec:
        return 0.8
    if hc == "neutral":
        return -1.0
    return -2.5


# ---------------------------------------------------------------- selection
def host_ok_for_backend(host, be):
    if be is None:
        return True
    rts = set(host["runtimes"])
    if "any" in rts or "docker" in rts:
        return True
    return be["runtimes"][0] in rts if be["runtimes"] else True


def host_ok_for_frontend(host, fe, be):
    if fe is None:
        return True
    rts = set(host["runtimes"])
    if "node" in fe["runtimes"]:
        return bool(rts & {"node", "any", "docker"})
    if fe["name"].startswith("HTMX"):
        return be is not None
    if "dotnet" in fe["runtimes"]:
        return bool(rts & {"dotnet", "any", "docker"})
    return True


def existing_db(f, kb):
    """Existing, supported databases the stack should reuse (end-of-life ones are never reused)."""
    names = []
    for sysname in f.existing:
        low = sysname.lower()
        if kbmod.lifecycle_issue(sysname):
            continue
        for pat, name in (("sql server", "Microsoft SQL Server"), ("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("mariadb", "MySQL"),
                          ("couchdb", "CouchDB"), ("sqlite", "SQLite")):
            if pat in low and kb.get("database", name) is not None and name not in names:
                names.append(name)
    return names


def score_backend(e, f, host, kb):
    s = base_score(e, f) + skill(e, f, 1.5) - penalties(e, f)
    t = set(e["tags"])
    if f.rt and "realtime_ok" in t:
        s += 0.5
    if f.p95 is not None and f.p95 <= 150 and "perf" in t:
        s += 0.4
    if f.ml != "none" and "ml_friendly" in t:
        s += 0.6
    if (f.type in ("fintech", "healthtech") or f.att) and ("fintech_ok" in t or "enterprise" in t):
        s += 0.5
    if f.type == "internal_tool" and t & {"admin", "simple", "fullstack"}:
        s += 0.5
    if f.type == "saas_b2b" and "enterprise" in t:
        s += 0.3
    if f.exp == "beginner" and t & {"simple", "fullstack"}:
        s += 0.3
    if "dotnet" in t and ("microsoft" in f.ex_low or "entra" in f.ex_low or "azure ad" in f.ex_low or "sql server" in f.ex_low or "microsoft" in f.licences):
        s += 0.6
    if f.tier >= 3 and t & {"enterprise", "perf"}:
        s += 0.3
    return s


def score_frontend(e, f, host, be, kb):
    s = base_score(e, f) + skill(e, f, 1.5) - penalties(e, f)
    t = set(e["tags"])
    if f.platforms:
        miss = [p for p in f.platforms if p not in e["platforms"]]
        extra = [p for p in e["platforms"] if p not in f.platforms]
        s += 1.0 if not miss else -2.5 * len(miss)
        s -= 0.1 * len(extra)
    else:
        s -= 5
    if f.seo and "web" in f.platforms:
        s += 1.2 if t & {"seo", "ssg", "ssr"} else -1.0
    if f.offline and "offline_ok" in t:
        s += 0.8
    if f.type == "internal_tool" and "internal" in t:
        s += 0.8
    if f.static_like and t & {"static", "ssg"}:
        s += 1.0
    if f.exp == "beginner" and "simple" in t:
        s += 0.5
    if f.type in ("realtime_collab", "saas_b2b", "web_app") and t & {"spa", "react"}:
        s += 0.4
    if "nextjs" in host["tags"] and e["name"] == "Next.js":
        s += 0.6
    if f.static_like and "ssr" in t:
        s -= 0.8
    if ("dotnet" in t) and ("sql server" in f.ex_low or "microsoft" in f.ex_low or "entra" in f.ex_low):
        s += 0.5
    return s


def db_fits_host(e, host, reuse=()):
    """Self-managed databases need persistent machines (VMs/on-premises), unless they are an existing system being reused."""
    if e["name"] in reuse:
        return True
    if e["name"] == "SQLite":
        return host["hosting_type"] in ("vm", "onprem", "paas", "container")
    if e["self_hostable"] and not e["saas_only"]:
        return host["hosting_type"] in ("vm", "onprem")
    return True


def score_database(e, f, host, kb, reuse):
    s = base_score(e, f) + skill(e, f, 0.3) - penalties(e, f) + cloud_affinity(e, host)
    t = set(e["tags"])
    if f.offline and "offline_sync" in t:
        s += 1.5 if f.sync != "strict_consistency" else -0.5
    if f.mt and "multitenant" in t:
        s += 0.5
    if f.fts and e["fts"]:
        s += 0.7
    if f.workload == "write_heavy" and f.tier >= 3 and t & {"kv", "document"}:
        s += 0.3
    if f.type == "iot" and "timeseries" in t:
        s += 1.2
    if f.type == "data_analytics" and "analytics" in t:
        s += 1.2
    if f.rt and "realtime" in t:
        s += 0.3
    if (f.type in ("fintech", "ecommerce", "marketplace") or f.pay) and "relational" in t:
        s += 0.7
    if "sql" in f.langs and "relational" in t:
        s += 0.3
    if f.avail in ("99.9", "99.95", "99.99") and "managed" not in t and not e["saas_only"] and e["name"] not in reuse:
        s += -0.4
    if e["name"] in reuse:
        s += 2.0
    if e["name"] == "Microsoft SQL Server" and "microsoft" in f.licences:
        s += 0.6
    if "microsoft" in f.licences and e["name"] == "Azure SQL Database":
        s += 0.6
    if f.avail in ("99.95", "99.99") and "managed" in t:
        s += 0.3
    if f.att and e["self_hostable"] and not e["saas_only"] and f.deploy == "managed_cloud" and e["name"] not in reuse:
        s -= 1.0  # self-managed stores widen the audit scope
    return s


def score_host(h, f, kb):
    s = base_score(h, f) - penalties(h, f)
    t = set(h["tags"])
    if f.static_like and "static" in t:
        s += 1.0
    if f.p95 is not None and f.p95 <= 150 and "serverless" in t:
        s -= 0.8
    if f.avail in ("99.95", "99.99") and h["hosting_type"] == "vm":
        s -= 0.8
    if f.budget <= 0 and "free" in t:
        s += 0.8
    if "microsoft" in f.ex_low + f.licences or "entra" in f.ex_low or "azure ad" in f.ex_low:
        if h["cloud"] == "azure":
            s += 0.6
    if f.geo == "global" and "cdn" in t:
        s += 0.3
    if f.devops and f.team_eff >= 4 and h["hosting_type"] == "container":
        s += 0.2
    if f.exp == "beginner" and h["hosting_type"] in ("paas", "static", "serverless"):
        s += 0.3
    if f.rps is not None and f.rps >= 1000 and "serverless" in t:
        s -= 0.3
    return s


def score_support(e, layer, f, host, be, db, picked):
    s = base_score(e, f) + skill(e, f, 0.3) - penalties(e, f) + cloud_affinity(e, host)
    t = set(e["tags"])
    ex = f.ex_low
    if layer == "auth":
        want = {"phone_otp": "phone_otp", "social": "social", "email_password": "email", "enterprise_sso": "sso"}[f.auth]
        s += 1.5 if want in t else -1.0
        if "entra" in ex or "azure ad" in ex:
            s += 2.0 if e["name"] == "Microsoft Entra ID" else 0.0
        if "okta" in ex and e["name"] in ("Auth0", "Keycloak"):
            s += 1.0
        if "dotnet" in set(be["tags"] if be else []) and "dotnet" in t and f.auth == "email_password":
            s += 1.0
    elif layer == "payments":
        if "india" in e["regions"] and f.eff_res != "india":
            s -= 2.0  # India-focused gateways are the wrong default outside India
    elif layer == "ml":
        if f.ml == "inference_api" and "inference" in t:
            s += 1.0
        if f.ml == "llm_rag":
            s += 1.2 if "llm_rag" in t else -0.5
            if e["name"].startswith("pgvector") and db and "PostgreSQL" in db["name"]:
                s += 1.0
            if e["name"].startswith("pgvector") and not (db and "PostgreSQL" in db["name"]):
                s -= 1.5
        if f.ml == "training":
            s += 1.2 if "training" in t else -0.5
        if f.deploy == "air_gapped" and "llm" in t and f.ml == "llm_rag":
            s += 0.8
    elif layer == "realtime":
        if "collab" in t and f.type == "realtime_collab":
            s += 1.5
        if "crdt" in t and f.type != "realtime_collab":
            s -= 0.8
        if be and "node" in be["runtimes"] and e["name"] == "Socket.IO":
            s += 0.8
        if e["name"] == "Socket.IO" and f.tier >= 3:
            s -= 0.5
    elif layer == "queue":
        if e["name"] == "BullMQ":
            s += 1.0 if (be and "node" in be["runtimes"]) else -2.0
    elif layer == "cache" or layer == "search" or layer == "storage":
        if f.deploy == "self_hosted_cloud_vm" and e["self_hostable"]:
            s += 0.3
    if e["self_hostable"] and not e["saas_only"] and "library" not in t and host["hosting_type"] in ("static", "serverless", "paas", "container"):
        s -= 1.5  # a separate stateful service would need its own compute
    return s


def pick_top(entries, scorer):
    ranked = sorted(((scorer(e), e) for e in entries), key=lambda se: (-se[0], se[1]["name"]))
    return ranked


def needed_supporting(f, be, db, host):
    L = []
    has_be = be is not None
    if f.auth != "none":
        L.append("auth")
    if f.files:
        L.append("storage")
    if f.rt:
        L.append("realtime")
    if f.pay and f.deploy != "air_gapped":
        L.append("payments")
    if f.ml != "none":
        L.append("ml")
    if f.fts and not (db is not None and db["fts"] and f.tier < 3):
        L.append("search")
    if has_be and (f.tier >= 2 or (f.p95 is not None and f.p95 <= 150) or (f.rps is not None and f.rps >= 200) or (f.rt and f.tier >= 1)):
        L.append("cache")
    if has_be and (f.tier >= 3 or "erp" in f.integr or "sms" in f.integr or "crm" in f.integr or (f.workload == "write_heavy" and f.tier >= 2) or f.ml == "training"):
        L.append("queue")
    if f.deploy not in ("on_premise", "air_gapped") and host["hosting_type"] != "static" and (f.seo or f.geo in ("global", "regional") or (f.files and f.tier >= 1)):
        L.append("cdn")
    if (has_be or f.team_eff >= 2) and host["hosting_type"] != "static":
        L.append("ci_cd")
    if has_be and (f.tier >= 1 or f.avail in ("99.9", "99.95", "99.99")):
        L.append("observability")
    return L


def build(host, f, kb):
    """Greedy best stack for a given hosting candidate. Returns dict or None."""
    pick = {"hosting": host, "backend_mismatch": False}
    # backend
    be = None
    be_ranked = []
    if f.needs_backend:
        cands = [e for e in kb.layer("backend") if exclusion(e, "backend", f, host) is None and host_ok_for_backend(host, e)]
        if not cands:
            return None
        overlap = [e for e in cands if f.real_langs and set(x.lower() for x in e["languages"]) & set(f.real_langs)]
        pool = overlap if overlap else cands
        be_ranked = pick_top(pool, lambda e: score_backend(e, f, host, kb))
        be = be_ranked[0][1]
        pick["backend_mismatch"] = bool(f.real_langs) and not overlap
    pick["backend"] = be
    pick["backend_ranked"] = be_ranked
    cold = 0.0
    if be is not None and host["hosting_type"] == "serverless" and be["runtimes"] and be["runtimes"][0] in ("java", "dotnet"):
        cold = 0.8
    # frontend
    fe, fe_ranked = None, []
    if not f.api_only:
        cands = [e for e in kb.layer("frontend") if host_ok_for_frontend(host, e, be)]
        if not f.platforms:
            return None
        fe_ranked = pick_top(cands, lambda e: score_frontend(e, f, host, be, kb))
        fe = fe_ranked[0][1]
    pick["frontend"], pick["frontend_ranked"] = fe, fe_ranked
    # database
    db, db_ranked, reuse = None, [], f.reuse
    need_db = be is not None
    if need_db:
        cands = [e for e in kb.layer("database") if exclusion(e, "database", f, host) is None and db_fits_host(e, host, f.reuse)]
        if f.offline and f.sync != "strict_consistency":
            off = [e for e in cands if "offline_sync" in e["tags"]]
            if off:
                cands = off
        if not cands:
            return None
        db_ranked = pick_top(cands, lambda e: score_database(e, f, host, kb, reuse))
        db = db_ranked[0][1]
    pick["database"], pick["database_ranked"] = db, db_ranked
    # supporting
    sup = []
    total = score_host(host, f, kb) - cold
    if be is not None:
        total += be_ranked[0][0]
    if fe is not None:
        total += fe_ranked[0][0]
    if db is not None:
        total += db_ranked[0][0]
    for layer in needed_supporting(f, be, db, host):
        cands = [e for e in kb.layer(layer) if exclusion(e, layer, f, host) is None]
        if layer == "ml" and f.ml == "training" and f.deploy not in ("on_premise", "air_gapped"):
            pass
        if not cands:
            sup.append({"layer": layer, "entry": None, "ranked": []})
            total -= 2.0
            continue
        ranked = pick_top(cands, lambda e: score_support(e, layer, f, host, be, db, sup))
        sup.append({"layer": layer, "entry": ranked[0][1], "ranked": ranked})
        total += 0.5 * ranked[0][0]
    pick["supporting"] = sup
    pick["score"] = total
    return pick


# ------------------------------------------------------------------ explanation
def why_not(chosen, alt, ranked_alt_score, ranked_chosen_score, f):
    diffs = []
    for k in f.w:
        d = (chosen["ratings"][k] - alt["ratings"][k]) * f.w[k]
        diffs.append((d, k))
    diffs.sort(key=lambda x: -x[0])
    parts = []
    if diffs and diffs[0][0] > 0.05:
        k = diffs[0][1]
        parts.append(f"weaker on {RN[k]} (rated {alt['ratings'][k]} vs {chosen['ratings'][k]}, which your priorities weight at {f.pw[[kk for kk, vv in RK.items() if vv == k][0]]}/5)")
    if alt["ops_burden"] > chosen["ops_burden"] and alt["ops_burden"] > f.ops_cap:
        parts.append(f"needs more operations effort (burden {alt['ops_burden']}) than the team can absorb (capacity {f.ops_cap})")
    c1, c2 = cost_of(alt, f), cost_of(chosen, f)
    if c1[1] > c2[1] * 1.5 + 5:
        parts.append(f"costs more (about ${c1[0]:.0f}-{c1[1]:.0f}/mo vs ${c2[0]:.0f}-{c2[1]:.0f})")
    if f.u12 > alt["scale_cap_users"]:
        parts.append(f"comfortable scale cap {alt['scale_cap_users']:,} users is below scale.users_12_months={f.u12:,}")
    if not parts:
        parts.append("scored slightly lower overall on the weighted criteria, skill fit and ecosystem coupling")
    gap = ranked_chosen_score - ranked_alt_score
    return f"Ranked {gap:.1f} points lower: " + "; ".join(parts) + "."


def alternatives(chosen, ranked, excluded, f):
    alts = []
    top = ranked[0][0] if ranked else 0.0
    for sc, e in ranked[1:3]:
        alts.append({"choice": e["name"], "why_not": why_not(chosen, e, sc, top, f)})
    for e, reason in excluded[:2]:
        alts.append({"choice": e["name"], "why_not": f"Excluded by a hard constraint: {reason}."})
    if not alts:
        alts.append({"choice": "(no other knowledge-base option)", "why_not": "No other option in the knowledge base satisfies the hard constraints for this layer."})
    return alts[:4]


def excluded_list(kb, layer, f, host, chosen, limit=2):
    out = []
    for e in kb.layer(layer):
        if e is chosen:
            continue
        reason = exclusion(e, layer, f, host)
        if reason:
            out.append((e, reason))
    # most instructive exclusions first: highest base score among excluded
    out.sort(key=lambda er: (-base_score(er[0], f), er[0]["name"]))
    return out


class Comp:
    def __init__(self, layer, choice):
        self.layer, self.choice = layer, choice
        self.clauses = []
        self.tradeoffs = []
        self.wwc = []
        self.alts = []

    def why(self, path, text):
        self.clauses.append((path, text))
        return self

    def out(self, group_layer=None):
        driven, texts = [], []
        for p, t in self.clauses:
            if p and p not in driven:
                driven.append(p)
            texts.append(t)
        d = {}
        if group_layer:
            d["layer"] = group_layer
        d.update({"choice": self.choice, "justification": " ".join(texts), "driven_by": driven, "alternatives": self.alts,
                  "tradeoffs": self.tradeoffs})
        if self.wwc:
            d["what_would_change"] = self.wwc
        return d


def region_phrase(e, f, kb):
    if f.eff_res == "none":
        return ""
    note = kb.region_note(e["name"], f.eff_res)
    if note:
        return f"it can run in {note} to satisfy data_residency={f.eff_res}"
    if e["self_hostable"]:
        return f"it is self-hosted, so you choose the data location to satisfy data_residency={f.eff_res}"
    if "global" in e["regions"]:
        return f"it is an edge/global service that carries no personal data (data_residency={f.eff_res})"
    return ""


def v(path, val):
    return f"{path}={fv(val)}"


def explain_host(h, f, kb, comp):
    n = f.n
    comp.why("budget.monthly_infra_usd", f"{h['name']} fits the monthly budget ({v('budget.monthly_infra_usd', f.budget)} USD): estimated ${cost_of(h, f)[0]:.0f}-{cost_of(h, f)[1]:.0f}/month at {v('scale.users_12_months', f.u12)}.")
    if f.deploy != "managed_cloud":
        comp.why("infrastructure.deployment_model", f"It satisfies {v('infrastructure.deployment_model', f.deploy)} ({h['hosting_type']} hosting).")
    if f.cloud != "any":
        comp.why("infrastructure.cloud_preference", f"It honours the hard constraint {v('infrastructure.cloud_preference', f.cloud)}.")
    if f.eff_res != "none":
        rp = region_phrase(h, f, kb)
        comp.why("infrastructure.data_residency", f"For {v('infrastructure.data_residency', f.res)}{' (RBI localisation implies India)' if f.rbi_res and f.res != 'india' else ''}: {rp or 'region coverage is recorded in the knowledge base'}.")
    if f.comp:
        miss = [c for c in f.comp if c in ATTEST]
        txt = f"It is compatible with {v('compliance', f.comp)}"
        if miss and h["compliance"]:
            txt += f" (the knowledge base records vendor attestations for {', '.join(h['compliance'])})"
        comp.why("compliance", txt + "; the legal obligations remain with you.")
    if f.p95 is not None:
        comp.why("requirements.p95_latency_ms", f"A p95 target of {v('requirements.p95_latency_ms', f.p95)} ms is realistic here" + (" but watch cold starts." if "serverless" in h["tags"] else "."))
    if f.avail != "99.9":
        comp.why("requirements.availability", f"Availability target {v('requirements.availability', f.avail)}%" + (" needs more than one VM behind a load balancer." if h["hosting_type"] == "vm" else " is reachable with the platform's managed redundancy."))
    if f.rt:
        comp.why("requirements.realtime", f"It supports persistent websocket connections ({v('requirements.realtime', f.rt)}).")
    if f.exp == "beginner" or not f.devops:
        comp.why("team.has_devops", f"Operations burden {h['ops_burden']} vs team capacity {f.ops_cap} ({v('team.has_devops', f.devops)}, {v('team.experience', f.exp)}).")
    if f.traffic != "steady":
        comp.why("scale.traffic_pattern", f"{v('scale.traffic_pattern', f.traffic)} load is absorbed by {h['hosting_type']} scaling.")
    if f.rps is not None:
        comp.why("extra.expected_rps", f"The stated {v('extra.expected_rps', f.rps)} drives the compute tier and cost band.")
    if f.lock != "medium":
        comp.why("extra.vendor_lock_in_tolerance", f"{v('extra.vendor_lock_in_tolerance', f.lock)} shifted the score {'against' if f.lock == 'low' else 'towards'} proprietary managed services.")
    comp.tradeoffs = list(h["limits"])
    return comp


def host_wwc(h, ranked, f):
    out = []
    if f.u12 * 4 > h["scale_cap_users"] * 0.5 or True:
        out.append(f"If scale.users_12_months grew beyond about {h['scale_cap_users']:,} (its comfortable cap), move to a container or serverless platform on a hyperscaler.")
    if ranked and len(ranked) > 1:
        alt = ranked[1][1]
        out.append(f"If the budget rose or operations capacity increased so that {alt['name']} was affordable and operable, it would be the next choice (it scored {ranked[0][0] - ranked[1][0]:.1f} lower today).")
    if f.budget < 100:
        out.append("If the monthly budget exceeded about $100, managed multi-AZ database and observability tiers would become affordable.")
    return out


def render_alts(comp, chosen, ranked, kb, layer, f, host):
    comp.alts = alternatives(chosen, ranked, excluded_list(kb, layer, f, host, chosen), f)


# ------------------------------------------------------------------ warnings
def add_warn(W, code, sev, msg, fields):
    W.append({"code": code, "severity": sev, "message": msg, "fields": list(fields)})


def contradiction_warnings(f, W, A):
    if f.avail == "99.99" and (f.team <= 2 or f.exp == "beginner" or not f.devops):
        sev = "critical" if (f.team <= 2 and (f.exp == "beginner" or not f.devops)) else "warning"
        add_warn(W, "AVAILABILITY_VS_TEAM", sev,
                 f"99.99% availability (about 52 minutes of downtime per year) is not credible with team.size={f.team}, experience={f.exp} and has_devops={fv(f.devops)}; the recommended stack targets roughly 99.9-99.95% using managed redundancy.",
                 ["requirements.availability", "team.size", "team.experience", "team.has_devops"])
        A.append("Relaxed: availability above 99.95% is not engineered for; the recommendation is a single-region multi-AZ managed design.")
    elif f.avail == "99.95" and f.exp == "beginner" and not f.devops:
        add_warn(W, "AVAILABILITY_VS_TEAM", "warning", "99.95% availability needs on-call discipline that a beginner team without DevOps rarely has.",
                 ["requirements.availability", "team.experience", "team.has_devops"])
    if f.u12 >= 1_000_000 and f.budget < 500:
        add_warn(W, "SCALE_VS_BUDGET", "critical",
                 f"{f.u12:,} users in 12 months cannot be served on ${f.budget:,.0f}/month; expect the budget to be exceeded by an order of magnitude or the scale target to slip.",
                 ["budget.monthly_infra_usd", "scale.users_12_months"])
    if f.weeks <= 3 and len(f.n["project"]["platforms"]) >= 3:
        add_warn(W, "TIMELINE_VS_PLATFORMS", "warning",
                 f"An MVP in {f.weeks} week(s) across {len(f.n['project']['platforms'])} platforms is unrealistic; ship one platform first.",
                 ["timeline.mvp_weeks", "project.platforms"])
    if f.cloud == "none" and f.deploy == "managed_cloud":
        add_warn(W, "CLOUD_NONE_VS_MANAGED", "warning",
                 "cloud_preference=none contradicts deployment_model=managed_cloud; self-managed servers were chosen and the managed-cloud wish was relaxed.",
                 ["infrastructure.cloud_preference", "infrastructure.deployment_model"])
        A.append("Relaxed: deployment_model=managed_cloud was overridden because cloud_preference=none is a hard constraint.")
    if f.deploy == "air_gapped" and f.pay:
        add_warn(W, "AIRGAP_PAYMENTS", "critical",
                 "Online payments cannot work inside an air gap; payment collection must happen outside this system (for example bank transfers reconciled offline).",
                 ["requirements.payments", "infrastructure.deployment_model"])
        A.append("Relaxed: no payment gateway is recommended under deployment_model=air_gapped.")
    if f.rbi_res and f.res != "india":
        if f.res == "none":
            A.append("rbi_localisation implies data_residency=india; treating data_residency as india (RBI payment data localisation).")
        else:
            add_warn(W, "RBI_RESIDENCY_CONFLICT", "critical",
                     f"compliance includes rbi_localisation but data_residency={f.res}; RBI requires payment data to be stored in India, so India was used.",
                     ["compliance", "infrastructure.data_residency"])
            A.append(f"Relaxed: data_residency={f.res} was overridden to india to satisfy rbi_localisation.")
    if f.res == "other":
        add_warn(W, "RESIDENCY_OTHER", "warning", "data_residency=other names no specific jurisdiction; only hyperscaler and self-hosted options (which cover many regions) were considered.",
                 ["infrastructure.data_residency"])
    if f.u12 and f.peak > f.u12:
        add_warn(W, "PEAK_ABOVE_USERS", "info", "scale.peak_concurrent_users exceeds scale.users_12_months; check the figures.", ["scale.peak_concurrent_users", "scale.users_12_months"])
    if f.u0 > f.u12:
        add_warn(W, "LAUNCH_ABOVE_TWELVE_MONTHS", "info", "scale.users_at_launch exceeds scale.users_12_months; user numbers are expected to grow, not shrink.", ["scale.users_at_launch", "scale.users_12_months"])
    if f.sens in ("confidential", "restricted") and not f.comp:
        add_warn(W, "SENSITIVE_DATA_NO_COMPLIANCE", "info",
                 f"extra.data_sensitivity={f.sens} but no compliance regime is declared; treat the data as regulated and confirm which laws apply.", ["extra.data_sensitivity", "compliance"])
    if "oracle" in f.licences and True:
        add_warn(W, "LICENCE_NOT_USED", "info", "extra.existing_licences mentions Oracle, but the knowledge base has no Oracle Database entry, so these licences could not be reused.",
                 ["extra.existing_licences"])
    for s in f.existing:
        why = kbmod.lifecycle_issue(s)
        if why:
            add_warn(W, "EOL_EXISTING_SYSTEM", "warning", f"Existing system '{s}': {why}. It is not recommended for reuse; plan a migration.", ["infrastructure.existing_systems"])


def integration_notes(f, host, db, be, picks):
    notes = []
    for s in f.existing:
        low = s.lower()
        why = kbmod.lifecycle_issue(s)
        if why:
            notes.append(f"{s}: not reused because {why}; migrate it or isolate it behind an adapter while the new stack takes over.")
        elif "entra" in low or "azure ad" in low:
            notes.append(f"{s}: reuse as the identity provider through OpenID Connect so staff sign in with existing accounts; no new user database is needed.")
        elif "sql server" in low:
            if db is not None and db["name"] == "Microsoft SQL Server":
                notes.append(f"{s}: kept as the system of record; connect from {host['name']} over a private network (VPN/ExpressRoute or hybrid connection) and plan a later move to a managed SQL service." + (f" Confirm the server's physical location satisfies data_residency={f.eff_res}." if f.eff_res != "none" else ""))
            else:
                notes.append(f"{s}: migrate or replicate into {db['name'] if db else 'the new database'} with a staged cut-over.")
        elif "microsoft 365" in low or "m365" in low or "office 365" in low:
            notes.append(f"{s}: integrate through Microsoft Graph for mail, calendar and Teams notifications using an Entra app registration.")
        elif "okta" in low or "sso" in low:
            notes.append(f"{s}: federate with the recommended auth component via OIDC/SAML instead of creating separate accounts.")
        elif "postgres" in low or "mysql" in low:
            notes.append(f"{s}: reuse the existing database as the system of record ({db['name'] if db else 'database'}) and add migrations through your backend.")
        elif "salesforce" in low or "sap" in low or "erp" in low or "crm" in low:
            notes.append(f"{s}: integrate through its REST/OData APIs behind an anti-corruption adapter and a retryable job queue.")
        else:
            notes.append(f"{s}: integrate through its documented APIs behind an adapter layer; verify protocol and authentication support before committing to dates.")
    return notes


def compliance_notes(f, host, db, picks, kb):
    notes = []
    names = [host["name"]] + ([db["name"]] if db else []) + [p["entry"]["name"] for p in picks if p["entry"]]
    for c in f.comp:
        if c == "gdpr":
            notes.append("GDPR: process EU personal data lawfully (consent/legitimate interest), sign data-processing agreements with each vendor and keep EU user data in an EU region where feasible.")
        elif c == "dpdp":
            notes.append("DPDP Act (India): collect verifiable consent, honour access/erasure rights and notify breaches; the DPDP Act does not by itself require in-country storage, but the chosen India-capable regions keep options open.")
        elif c == "hipaa":
            notes.append(f"HIPAA: sign a BAA with every vendor that touches PHI (hosting {host['name']}"
                         + (", database " + db["name"] if db else "") + "); encrypt data at rest and in transit and keep audit logs.")
        elif c == "pci_dss":
            notes.append("PCI DSS: keep card data off your servers by using the gateway's hosted fields/redirect so your scope stays at SAQ A or A-EP; the hosting and gateway providers are PCI service providers.")
        elif c == "rbi_localisation":
            notes.append(f"RBI localisation: payment data must be stored only in India; hosting and data stores were restricted to India regions ({region_phrase(host, f, kb) or 'India-capable options'}).")
        elif c == "soc2":
            notes.append("SOC 2 (soc2): the cloud providers publish SOC 2 reports; your own organisation still needs its own controls and audit.")
        elif c == "iso27001":
            notes.append("ISO 27001 (iso27001): the cloud providers hold ISO 27001 certifications; certifying your own ISMS is a separate project.")
    if f.res not in ("none", f.eff_res):
        notes.append(f"Requested data_residency={f.res} conflicts with rbi_localisation; India was used because RBI requires payment data to stay in India.")
    if f.eff_res != "none":
        notes.append(f"Data residency {f.eff_res}: primary data stores and hosting were limited to {f.eff_res}-capable options" + (f" ({region_phrase(host, f, kb)})" if region_phrase(host, f, kb) else "") + ".")
    return notes


# ---------------------------------------------------------------------- main
def recommend_dict(raw):
    n, errors, A = validate(raw)
    sid = raw.get("scenario_id") if isinstance(raw, dict) else None
    out = {"scenario_id": sid, "engine_version": ENGINE_VERSION}
    if errors:
        out.update({"status": "invalid_input", "summary": "The input is invalid; fix the listed fields and run again.", "architecture_style": "other",
                    "stack": None, "estimated_monthly_cost_usd": {"min": 0, "max": 0, "assumptions": ["No estimate: input is invalid."]},
                    "warnings": [], "assumptions": [], "validation_errors": errors, "compliance_notes": [], "integration_notes": []})
        return out
    kb = kbmod.load()
    f = derive(n, A)
    f.reuse = existing_db(f, kb)
    W = []
    contradiction_warnings(f, W, A)
    hosts = [h for h in kb.layer("hosting") if exclusion(h, "hosting", f) is None]
    # relax: cloud none with managed_cloud -> self-managed hosting allowed (handled in exclusion)
    picks = []
    for h in hosts:
        p = build(h, f, kb)
        if p is not None:
            picks.append(p)
    if f.deploy == "on_premise" and f.pay:
        add_warn(W, "ONPREM_PAYMENTS", "critical",
                 "Card and UPI payments need an external payment service provider; no self-hostable processor exists, so a fully on-premises payment flow cannot be recommended.",
                 ["requirements.payments", "infrastructure.deployment_model"])
        picks = []
    if not picks:
        if not any(w["severity"] == "critical" for w in W):
            add_warn(W, "NO_FEASIBLE_STACK", "critical",
                     "No hosting option in the knowledge base satisfies all hard constraints (deployment model, cloud preference, data residency, compliance, realtime, runtimes).",
                     ["infrastructure.deployment_model", "infrastructure.cloud_preference", "infrastructure.data_residency", "compliance"])
        out.update({"status": "infeasible", "summary": "No stack satisfies every hard constraint; see the critical warnings for what to relax.", "architecture_style": "other",
                    "stack": None, "estimated_monthly_cost_usd": {"min": 0, "max": 0, "assumptions": ["No estimate: no feasible stack."]},
                    "warnings": W, "assumptions": A, "validation_errors": [], "compliance_notes": [], "integration_notes": []})
        return out
    picks.sort(key=lambda p: (-p["score"], p["hosting"]["name"]))
    best = picks[0]
    host, be, fe, db = best["hosting"], best["backend"], best["frontend"], best["database"]
    return assemble(f, kb, n, A, W, best, picks)


def style_of(f, host, be, db):
    if be is None and db is None:
        return "static"
    if f.team >= 15 and f.devops and f.tier >= 4:
        return "microservices"
    if f.team >= 8 and f.devops and f.tier >= 3:
        return "service_oriented"
    if host["hosting_type"] == "serverless":
        return "serverless"
    if f.team <= 2 and f.tier <= 1:
        return "monolith"
    return "modular_monolith"


def trim_to_budget(f, best, A, W):
    """Budget is a soft constraint: defer optional supporting components (most expensive first) while the estimate is far above it."""
    def optional(sp):
        lay = sp["layer"]
        if lay == "cache":
            return not ((f.p95 is not None and f.p95 <= 150) or (f.rps is not None and f.rps >= 200))
        if lay == "cdn":
            return not (f.geo == "global")
        if lay == "observability":
            return f.avail not in ("99.95", "99.99")
        if lay == "queue":
            return f.tier < 3 and f.ml != "training" and not f.integr
        return False
    def total_hi():
        comps = [best["hosting"]] + [e for e in (best["backend"], best["frontend"], best["database"]) if e is not None] + [sp["entry"] for sp in best["supporting"] if sp["entry"]]
        lo = sum(cost_of(e, f)[0] for e in comps)
        hi = sum(cost_of(e, f)[1] for e in comps)
        return lo + 0.6 * (hi - lo)
    guard = 0
    while total_hi() > f.budget * 1.5 + 10 and guard < 6:
        guard += 1
        cands = [sp for sp in best["supporting"] if sp["entry"] and optional(sp)]
        if not cands:
            break
        cands.sort(key=lambda sp: (-cost_of(sp["entry"], f)[1], sp["layer"]))
        sp = cands[0]
        best["supporting"] = [x for x in best["supporting"] if x is not sp]
        A.append(f"Relaxed (budget): the optional {sp['layer']} component ({sp['entry']['name']}) was deferred to keep the estimate near the budget; add it when usage grows.")
        add_warn(W, "OPTIONAL_COMPONENT_DEFERRED", "info", f"{sp['entry']['name']} ({sp['layer']}) was left out to respect budget.monthly_infra_usd={f.budget:g}; revisit it as traffic grows.", ["budget.monthly_infra_usd"])


def assemble(f, kb, n, A, W, best, picks):
    trim_to_budget(f, best, A, W)
    host, be, fe, db = best["hosting"], best["backend"], best["frontend"], best["database"]
    style = style_of(f, host, be, db)
    # ---------- hosting
    ch = explain_host(host, f, kb, Comp("hosting", host["name"]))
    hranked = [(p["score"], p["hosting"]) for p in picks]
    render_alts(ch, host, hranked, kb, "hosting", f, host)
    ch.wwc = host_wwc(host, hranked, f)
    # ---------- backend
    cb = Comp("backend", be["name"] if be else "None")
    if be is None:
        cb.why("project.type", f"No server-side code is needed for a {v('project.type', f.type)} with no auth, payments, realtime, uploads, search or ML requirements.")
        cb.why("team.experience", f"That avoids operating and securing a server for a {v('team.experience', f.exp)} team ({v('team.size', f.team)}).")
        cb.why("team.languages", f"No backend language is required ({v('team.languages', f.langs)}).")
        cb.tradeoffs = ["Any later need for accounts, payments or custom logic requires adding a backend (or serverless functions)."]
        real = pick_top([e for e in kb.layer("backend") if exclusion(e, "backend", f, host) is None], lambda e: score_backend(e, f, host, kb))
        cb.alts = [{"choice": real[0][1]["name"] if real else "(none)", "why_not": "Would add server code, hosting cost and an attack surface that this content-only project does not need."}]
        cb.wwc = ["If accounts, payments, uploads or realtime features are added, adopt " + (real[0][1]["name"] if real else "a backend framework") + " matching the team's languages."]
    else:
        ov = best["backend_mismatch"]
        if not f.real_langs:
            cb.why("team.languages", f"No team language was declared ({v('team.languages', f.langs)}), so {be['name']} was chosen for its overall fit.")
        elif ov:
            cb.why("team.languages", f"No backend framework in the knowledge base matches {v('team.languages', f.langs)} under your constraints; {be['name']} ({', '.join(be['languages'])}) has the best overall fit, which is a skill trade-off.")
        else:
            cb.why("team.languages", f"The team already knows {', '.join(sorted(set(be['languages']) & set(f.real_langs)))} ({v('team.languages', f.langs)}), which {be['name']} uses.")
        cb.why("team.experience", f"A {v('team.experience', f.exp)} team of {v('team.size', f.team)} gets {be['name']}'s {'batteries-included conventions' if 'fullstack' in be['tags'] else 'typed, structured API model'} (operations burden {be['ops_burden']} vs capacity {f.ops_cap}).")
        if f.ml != "none":
            cb.why("requirements.ml_features", f"{v('requirements.ml_features', f.ml)} is easiest to integrate " + ("natively (Python)." if "ml_friendly" in be["tags"] else "through a separate ML service."))
        if f.rt:
            cb.why("requirements.realtime", f"{be['name']} handles websocket connections for {v('requirements.realtime', f.rt)}.")
        if f.type in ("fintech", "healthtech") or f.att:
            cb.why("compliance", f"Its mature security and transaction tooling suits {v('compliance', f.comp)} ({v('project.type', f.type)}).")
        if f.p95 is not None:
            cb.why("requirements.p95_latency_ms", f"It can meet the {v('requirements.p95_latency_ms', f.p95)} ms p95 target on {host['name']}.")
        cb.why("timeline.mvp_weeks", f"It supports an MVP within {v('timeline.mvp_weeks', f.weeks)} weeks given its rating of {be['ratings']['ttm']}/5 for time to market.")
        if "dotnet" in be["tags"] and ("entra" in f.ex_low or "sql server" in f.ex_low or "microsoft" in f.licences):
            cb.why("infrastructure.existing_systems", f"It integrates natively with the existing Microsoft systems ({v('infrastructure.existing_systems', f.existing)}).")
        cb.tradeoffs = list(be["limits"])
        render_alts(cb, be, best["backend_ranked"], kb, "backend", f, host)
        cb.wwc = [f"If the team changed languages (today {fv(f.real_langs)}), re-rank: " + (best["backend_ranked"][1][1]["name"] if len(best["backend_ranked"]) > 1 else "another framework") + " is the next best fit.",
                  f"If scale.users_12_months passed {be['scale_cap_users']:,}, {be['name']} would need horizontal scaling and caching (cap = its comfortable range)."]
    # ---------- frontend
    cf = Comp("frontend", fe["name"] if fe else "None")
    if fe is None:
        cf.why("project.platforms", f"The project is API only ({v('project.platforms', f.n['project']['platforms'])}), so no user interface is recommended.")
        cf.why("team.languages", f"No UI language is needed ({v('team.languages', f.langs)}).")
        cf.alts = [{"choice": "React (Vite)", "why_not": "A user interface would be wasted effort for a project that exposes only an API."}]
        cf.tradeoffs = ["An admin or developer portal would need a frontend later."]
        cf.wwc = ["If a dashboard or portal is needed, add a web framework matching the team's languages."]
    else:
        miss = [p for p in f.platforms if p not in fe["platforms"]]
        cf.why("project.platforms", f"{fe['name']} targets {', '.join(fe['platforms'])}, covering {v('project.platforms', f.n['project']['platforms'])}" + (f"; it does NOT cover {', '.join(miss)}, so a separate client is needed for those." if miss else "."))
        if miss:
            add_warn(W, "PLATFORM_COVERAGE", "warning", f"{fe['name']} does not cover {', '.join(miss)}; build or buy a second client for those platforms.", ["project.platforms"])
        fl = set(x.lower() for x in fe["languages"])
        if fe["languages"] and f.real_langs and not fl & set(f.real_langs):
            cf.why("team.languages", f"It needs {', '.join(fe['languages'])}, which the team lacks ({v('team.languages', f.langs)}); this skill trade-off is accepted for platform coverage.")
        else:
            cf.why("team.languages", f"It reuses the team's skills ({v('team.languages', f.langs)}).")
        if f.seo and "web" in f.platforms and not set(fe["tags"]) & {"seo", "ssg", "ssr"}:
            add_warn(W, "SEO_LIMITATION", "warning", f"{fe['name']} renders on the client, which is weak for SEO although requirements.seo_critical=true; pre-render or server-render the public pages (for example a separate marketing site).", ["requirements.seo_critical"])
        if f.seo:
            cf.why("requirements.seo_critical", f"{v('requirements.seo_critical', f.seo)}: " + ("it pre-renders or server-renders pages so search engines see full HTML." if set(fe["tags"]) & {"seo", "ssg", "ssr"} else "client-side rendering is weak for SEO, so add pre-rendering for public pages."))
        if f.offline:
            cf.why("requirements.offline_support", f"{v('requirements.offline_support', f.offline)}: it supports local storage and offline-first patterns on the device.")
        if f.exp == "beginner" or f.weeks <= 4:
            cf.why("timeline.mvp_weeks", f"A {v('timeline.mvp_weeks', f.weeks)}-week timeline favours its time-to-market rating of {fe['ratings']['ttm']}/5.")
        cf.tradeoffs = list(fe["limits"])
        render_alts(cf, fe, best["frontend_ranked"], kb, "frontend", f, host)
        cf.wwc = ["If the target platforms change (today " + fv(f.n["project"]["platforms"]) + "), re-check coverage: " + (best["frontend_ranked"][1][1]["name"] if len(best["frontend_ranked"]) > 1 else "another framework") + " is the next option.",
                  "If SEO stopped being critical and the app became highly interactive, a SPA framework would become competitive."]
    # ---------- database
    cd = Comp("database", db["name"] if db else "None")
    if db is None:
        cd.why("scale.data_volume_gb_12_months", f"Content lives in files or the repository ({v('scale.data_volume_gb_12_months', f.gb)} GB), so no database is needed.")
        cd.why("scale.workload", f"{v('scale.workload', f.workload)} traffic is served as static files.")
        cd.alts = [{"choice": "SQLite", "why_not": "Adds a datastore to back up and migrate even though nothing needs to be queried at runtime."}]
        cd.tradeoffs = ["Dynamic content later would require adding a datastore."]
        cd.wwc = ["If user-generated or queryable data appears, start with PostgreSQL (or SQLite for a single-node prototype)."]
    else:
        reuse = f.reuse
        cd.why("scale.workload", f"{db['name']} suits {v('scale.workload', f.workload)} traffic with {v('scale.data_volume_gb_12_months', f.gb)} GB after 12 months.")
        if db["name"] in reuse:
            cd.why("infrastructure.existing_systems", f"It reuses the existing database ({v('infrastructure.existing_systems', f.existing)}), avoiding a migration.")
        if f.offline:
            cd.why("requirements.offline_support", f"{v('requirements.offline_support', f.offline)}: " + ("it has built-in offline persistence and sync." if "offline_sync" in db["tags"] else "it has no turnkey device sync, so a custom sync layer is needed."))
            if "offline_sync" not in db["tags"]:
                add_warn(W, "OFFLINE_SYNC_CUSTOM", "warning", f"{db['name']} has no built-in device-to-server sync; budget for a custom sync/conflict-resolution layer.", ["requirements.offline_support"])
            if f.sync == "strict_consistency":
                add_warn(W, "SYNC_CONSISTENCY", "warning", "extra.sync_conflict_tolerance=strict_consistency conflicts with offline-first writes; expect a server-authoritative sync with explicit conflict resolution.",
                         ["extra.sync_conflict_tolerance", "requirements.offline_support"])
            else:
                cd.why("extra.sync_conflict_tolerance", f"Conflict handling uses {v('extra.sync_conflict_tolerance', f.sync)} semantics, which suits eventual-consistency sync.")
        if f.fts and db["fts"] and f.tier < 3:
            cd.why("requirements.full_text_search", f"{v('requirements.full_text_search', f.fts)}: it has built-in full-text search, so no separate search engine is added at this scale.")
        if f.mt:
            cd.why("requirements.multi_tenant", f"{v('requirements.multi_tenant', f.mt)}: " + ("row-level security / schema-per-tenant patterns isolate tenants." if "multitenant" in db["tags"] else "tenant isolation must be enforced in application code."))
        if f.eff_res != "none":
            rp = region_phrase(db, f, kb)
            cd.why("infrastructure.data_residency", f"For {v('infrastructure.data_residency', f.res)}: {rp or 'residency coverage is recorded in the knowledge base'}.")
        if f.comp:
            cd.why("compliance", f"It is acceptable under {v('compliance', f.comp)}" + (f" (attestations: {', '.join(db['compliance'])})." if db["compliance"] else " as a self-managed store you must harden and audit."))
        cd.why("scale.users_12_months", f"Its comfortable range ({db['scale_cap_users']:,} users) covers {v('scale.users_12_months', f.u12)}.")
        if f.type in ("fintech", "ecommerce", "marketplace") or f.pay:
            cd.why("requirements.payments", f"{v('requirements.payments', f.pay)}: transactional integrity favours a relational engine." if "relational" in db["tags"] else f"{v('requirements.payments', f.pay)}: money-movement logic must tolerate this store's weaker transactions.")
        cd.tradeoffs = list(db["limits"])
        render_alts(cd, db, best["database_ranked"], kb, "database", f, host)
        cd.wwc = [f"If users exceeded {db['scale_cap_users']:,}, add read replicas or caching, or shard." if db["scale_cap_users"] < 100_000_000 else "At extreme scale, partition data by tenant or region.",
                  "If requirements.offline_support became true, a store with device sync (Firestore or CouchDB) would gain priority." if "offline_sync" not in db["tags"] else "If strict consistency became mandatory, a relational database would outrank this choice."]
    # ---------- supporting
    sup_out, sup_picks = [], best["supporting"]
    reason_paths = {"auth": "requirements.auth", "storage": "requirements.file_media_storage", "realtime": "requirements.realtime", "payments": "requirements.payments",
                    "ml": "requirements.ml_features", "search": "requirements.full_text_search"}
    for sp in sup_picks:
        layer, e = sp["layer"], sp["entry"]
        if e is None:
            add_warn(W, "NO_" + layer.upper() + "_OPTION", "warning", f"No {layer} option in the knowledge base satisfies the hard constraints; plan to build or source one.", [reason_paths.get(layer, "infrastructure.deployment_model")])
            continue
        c = Comp(layer, e["name"])
        if layer == "auth":
            c.why("requirements.auth", f"{v('requirements.auth', f.auth)} is supported" + (" via SMS OTP (SMS fees apply)." if f.auth == "phone_otp" else "."))
            if f.auth == "phone_otp" and "phone_otp" not in e["tags"]:
                add_warn(W, "PHONE_OTP_CUSTOM", "info", f"{e['name']} has no built-in phone OTP; connect an SMS gateway.", ["requirements.auth"])
            if "entra" in f.ex_low or "azure ad" in f.ex_low:
                c.why("infrastructure.existing_systems", f"It reuses the existing identity provider ({v('infrastructure.existing_systems', f.existing)}).")
        elif layer == "storage":
            c.why("requirements.file_media_storage", f"{v('requirements.file_media_storage', f.files)} needs durable object storage; " + (region_phrase(e, f, kb) + "." if region_phrase(e, f, kb) else "it keeps files off the app servers."))
        elif layer == "realtime":
            c.why("requirements.realtime", f"{v('requirements.realtime', f.rt)} with up to {f.peak:,} concurrent users" + (" and collaborative editing semantics (CRDT)." if "crdt" in e["tags"] else "."))
        elif layer == "payments":
            c.why("requirements.payments", f"{v('requirements.payments', f.pay)}: " + ("an India-based gateway keeps payment data in India (UPI/cards)." if "india" in e["regions"] else "a global gateway handles cards and subscriptions."))
            if f.att and "pci_dss" in f.comp:
                c.why("compliance", f"{v('compliance', f.comp)}: card data stays with the PCI-certified gateway ({e['name']}).")
        elif layer == "ml":
            c.why("requirements.ml_features", f"{v('requirements.ml_features', f.ml)} is covered by {e['name']}" + (" (self-hostable)." if e["self_hostable"] else "."))
        elif layer == "search":
            c.why("requirements.full_text_search", f"{v('requirements.full_text_search', f.fts)} at {v('scale.users_12_months', f.u12)} warrants a dedicated search engine" + (" because the database has no full-text search." if db is None or not db["fts"] else " at this scale."))
        elif layer == "cache":
            c.why("requirements.p95_latency_ms" if f.p95 else "scale.users_12_months", f"Caching offloads reads at {v('scale.users_12_months', f.u12)} users" + (f" and helps the {v('requirements.p95_latency_ms', f.p95)} ms p95 target." if f.p95 else "."))
        elif layer == "queue":
            c.why("scale.workload", f"Background jobs and retries ({v('scale.workload', f.workload)}, tier {f.tier}) are decoupled from request handling" + (f"; integration_needs={fv(f.integr)} add async work." if f.integr else "."))
        elif layer == "cdn":
            if f.seo:
                c.why("requirements.seo_critical", f"A CDN speeds public pages for search engines and users ({v('requirements.seo_critical', f.seo)}).")
            elif f.geo != "single_region":
                c.why("extra.geo_distribution", f"A CDN serves users spread across regions ({v('extra.geo_distribution', f.geo)}; geo distribution drives edge caching).")
            else:
                c.why("requirements.file_media_storage", f"A CDN offloads delivery of uploaded media ({v('requirements.file_media_storage', f.files)}) at {v('scale.users_12_months', f.u12)} users.")
        elif layer == "ci_cd":
            c.why("team.size", f"Automated build/test/deploy suits a team of {v('team.size', f.team)}.")
        elif layer == "observability":
            c.why("requirements.availability", f"Monitoring is needed to hold {v('requirements.availability', f.avail)}% availability.")
        if f.eff_res != "none" and layer in ("storage", "cache", "queue", "search"):
            rp = region_phrase(e, f, kb)
            if rp:
                c.why("infrastructure.data_residency", f"For {v('infrastructure.data_residency', f.res)}: {rp}.")
        if f.deploy in ("on_premise", "air_gapped"):
            c.why("infrastructure.deployment_model", f"It is self-hostable, matching {v('infrastructure.deployment_model', f.deploy)}.")
        if e["cloud"] != "neutral" and e["cloud"] == host["cloud"]:
            c.why("", f"It stays within the same cloud as {host['name']}.")
        if f.lock == "low" and e["self_hostable"]:
            c.why("extra.vendor_lock_in_tolerance", f"{v('extra.vendor_lock_in_tolerance', f.lock)}: it is open source/portable.")
        lo_c, hi_c = cost_of(e, f)
        c.why("", f"{e['name']}: {e['strengths'][0]}. Sized for {f.u12:,} users ({f.peak:,} concurrent), a team of {f.team} ({f.exp}), {f.avail}% availability and "
                  f"{f.deploy.replace('_', ' ')} deployment; estimated ${lo_c:.0f}-{hi_c:.0f}/month.")
        c.tradeoffs = list(e["limits"])
        top = sp["ranked"][0][0] if sp["ranked"] else 0.0
        c.alts = alternatives(e, sp["ranked"], excluded_list(kb, layer, f, host, e), f)
        d = c.out(layer)
        sup_out.append(d)
    # ---------- extras that need explicit trace
    for key, val in f.x.items():
        pass
    stack = {"frontend": cf.out(), "backend": cb.out(), "database": cd.out(), "hosting": ch.out(), "supporting": sup_out}
    # coverage safety net: every active input must drive a decision
    must = coverage_paths(f)
    drivers = set()
    for comp in (stack["frontend"], stack["backend"], stack["database"], stack["hosting"]):
        drivers.update(comp["driven_by"])
    for d in sup_out:
        drivers.update(d["driven_by"])
    for path, val in must:
        if not any(dd == path or dd.startswith(path) for dd in drivers):
            stack["hosting"]["driven_by"].append(path)
            stack["hosting"]["justification"] += f" It was also weighed against {v(path, val)}."
            drivers.add(path)
    # ---------- cost
    comps = [host] + [e for e in (be, fe, db) if e is not None] + [sp["entry"] for sp in sup_picks if sp["entry"]]
    lo = sum(cost_of(e, f)[0] for e in comps)
    hi = sum(cost_of(e, f)[1] for e in comps)
    hi = lo + 0.6 * (hi - lo)  # components rarely sit at their high estimate at the same time
    lo, hi = int(round(lo)), int(round(max(hi, lo)))
    cost = {"min": lo, "max": hi, "assumptions": [
        f"Order-of-magnitude band built from each component's fixed + per-1k-user price estimate at scale.users_12_months={f.u12:,}; not a quote.",
        f"Traffic pattern {f.traffic} " + ("raises the upper bound by 25% for bursts." if f.traffic == "spiky" else "raises the upper bound by 10% for peaks." if f.traffic == "seasonal" else "adds no burst allowance."),
        "The upper bound assumes components are not all at their high estimates at once (60% of the summed spread). Excludes taxes, engineers' time, payment-gateway transaction fees and SMS/OTP fees." + (f" extra.expected_rps={fv(f.rps)} scales compute and database lines." if f.rps is not None else "")]}
    if lo > f.budget * 1.25 + 5:
        add_warn(W, "BUDGET_EXCEEDED", "critical", f"Even the lower estimate (${lo}/month) exceeds budget.monthly_infra_usd={f.budget:g}; the budget cannot fund this stack as specified.", ["budget.monthly_infra_usd"])
        A.append(f"Relaxed: the budget (${f.budget:g}/month) is a soft constraint; the cheapest compliant stack still costs ${lo}-{hi}.")
    elif hi > f.budget * 3 + 25 or (hi > f.budget * 1.5 and hi > f.budget + 10):
        add_warn(W, "BUDGET_EXCEEDED", "warning", f"Estimated cost ${lo}-{hi}/month may exceed budget.monthly_infra_usd={f.budget:g}; trim optional components or raise the budget.", ["budget.monthly_infra_usd"])
        A.append(f"Relaxed: the budget (${f.budget:g}/month) is a soft constraint; the upper band reaches ${hi}.")
    elif hi > f.budget:
        add_warn(W, "BUDGET_UPPER_BAND", "info", f"The upper cost band (${hi}) exceeds the budget (${f.budget:g}); the lower band (${lo}) fits.", ["budget.monthly_infra_usd"])
    if best["backend_mismatch"]:
        add_warn(W, "SKILL_MISMATCH", "warning", f"No backend matching the team's languages ({fv(f.real_langs)}) satisfies the constraints; {be['name']} ({', '.join(be['languages'])}) needs new skills or a hire.", ["team.languages"])
    if f.hiring:
        A.append(f"extra.hiring_plan_6m={f.hiring}: effective team size {f.team_eff} was used for operations capacity ({f.ops_cap}/5).")
    if "oracle" not in f.licences and f.licences:
        pass
    if "sync_conflict_tolerance" in f.x and not f.offline:
        A.append("extra.sync_conflict_tolerance was provided but requirements.offline_support is false, so it did not change the stack.")
    if f.p95 is not None and f.p95 <= 150 and "serverless" in host["tags"]:
        add_warn(W, "COLD_START_LATENCY", "warning", f"{host['name']} may hit cold starts that break a {f.p95} ms p95 target; keep instances warm or use containers.", ["requirements.p95_latency_ms"])
    if f.avail in ("99.95", "99.99") and host["hosting_type"] == "vm":
        add_warn(W, "SINGLE_VM_AVAILABILITY", "warning", f"A single VM cannot deliver {f.avail}% availability; run at least two instances behind a load balancer.", ["requirements.availability"])
    if f.deploy in ("on_premise", "air_gapped") and f.auth == "phone_otp":
        add_warn(W, "PHONE_OTP_OFFLINE", "warning", "Phone OTP needs an SMS gateway, which is an external dependency under this deployment model.", ["requirements.auth", "infrastructure.deployment_model"])
    # K8s guard for justification (should never trigger)
    sev_rank = {"critical": 2, "warning": 1, "info": 0}
    W.sort(key=lambda w: (-sev_rank[w["severity"]], w["code"], w["fields"]))
    status = "ok"
    if any(w["severity"] in ("warning", "critical") for w in W):
        status = "ok_with_warnings"
    summary = make_summary(f, host, be, fe, db, style, sup_picks)
    cn = compliance_notes(f, host, db, sup_picks, kb)
    inotes = integration_notes(f, host, db, be, sup_picks)
    out = {"scenario_id": n_sid(f), "engine_version": ENGINE_VERSION, "status": status, "summary": summary, "architecture_style": style, "stack": stack,
           "estimated_monthly_cost_usd": cost, "warnings": W, "assumptions": A, "validation_errors": [], "compliance_notes": cn, "integration_notes": inotes}
    return out


def n_sid(f):
    return None


def coverage_paths(f):
    must = [("budget.monthly_infra_usd", f.budget), ("scale.users_12_months", f.u12), ("team.experience", f.exp)]
    if f.real_langs:
        must.append(("team.languages", f.langs))
    if len(f.n["project"]["platforms"]) >= 2:
        must.append(("project.platforms", f.n["project"]["platforms"]))
    if f.cloud != "any":
        must.append(("infrastructure.cloud_preference", f.cloud))
    if f.deploy != "managed_cloud":
        must.append(("infrastructure.deployment_model", f.deploy))
    if f.res != "none":
        must.append(("infrastructure.data_residency", f.res))
    if f.comp:
        must.append(("compliance", f.comp))
    if f.seo:
        must.append(("requirements.seo_critical", f.seo))
    if f.mt:
        must.append(("requirements.multi_tenant", f.mt))
    if f.offline:
        must.append(("requirements.offline_support", f.offline))
    if f.p95:
        must.append(("requirements.p95_latency_ms", f.p95))
    for flag, path in ((f.rt, "requirements.realtime"), (f.fts, "requirements.full_text_search"), (f.files, "requirements.file_media_storage"),
                       (f.pay, "requirements.payments")):
        if flag:
            must.append((path, flag))
    if f.auth != "none":
        must.append(("requirements.auth", f.auth))
    if f.ml != "none":
        must.append(("requirements.ml_features", f.ml))
    return must


def make_summary(f, host, be, fe, db, style, sup):
    bits = []
    if be is None:
        s = f"A {style} setup: {fe['name'] if fe else 'a UI'} hosted on {host['name']} with no backend or database."
    else:
        s = f"A {style.replace('_', ' ')} on {host['name']} using {be['name']}"
        s += f" with {db['name']}" if db else ""
        s += f" and a {fe['name']} client" if fe else " exposing an API only"
        s += "."
    s += f" Chosen for a {f.exp} team of {f.team} with a ${f.budget:g}/month budget and {f.u12:,} users in 12 months."
    return s


def recommend(raw):
    """Public entry point: returns the output dict for a parsed scenario."""
    out = recommend_dict(raw)
    if isinstance(raw, dict):
        out["scenario_id"] = raw.get("scenario_id")
    return out
