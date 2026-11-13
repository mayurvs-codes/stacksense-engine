"""Heuristic scan over fuzzed scenarios for known-bad patterns (beyond the gate oracle). Usage: python tools/scan.py SEED N"""
import sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gate")); sys.path.insert(0, str(ROOT))
import run_gate, oracle
from stacksense import recommend, kb as K
kb = K.load(); okb = oracle.load_kb()
seed, n = int(sys.argv[1]), int(sys.argv[2])
DYN = {"web_app", "saas_b2b", "ecommerce", "marketplace", "social", "realtime_collab", "fintech", "healthtech", "data_analytics", "iot", "ai_ml_product", "internal_tool", "gaming", "api_platform"}
PERSIST = {"vm", "onprem"}
sus = collections.Counter(); ex = collections.defaultdict(list); bad = 0; viable = 0
for s in run_gate.gen_scenarios(n, seed):
    o = recommend(s)
    v = oracle.violations(s, o, okb) if o["status"] != "invalid_input" else []
    if v:
        bad += 1; ex["oracle"].append((s["scenario_id"], v[:2]))
    st = o["stack"]
    if not st:
        continue
    viable += 1
    fe, be, db, ho = (st[k]["choice"] for k in ("frontend", "backend", "database", "hosting"))
    t, r, sid = s["project"]["type"], s["requirements"], s["scenario_id"]
    hk = kb.get("hosting", ho); dk = kb.get("database", db) if db != "None" else None
    sup = [(c["layer"], c["choice"]) for c in st["supporting"]]
    def flag(name):
        sus[name] += 1; ex[name].append(sid)
    if fe in ("Astro", "Eleventy") and t in DYN: flag("static generator for dynamic app")
    if dk and ({"document", "kv"} & set(dk["tags"])) and not (r["offline_support"] or t in ("gaming", "social", "iot")): flag("non-relational without need")
    if db == "SQLite" and hk["hosting_type"] not in PERSIST: flag("sqlite on ephemeral host")
    if dk and dk["self_hostable"] and not dk["saas_only"] and hk["hosting_type"] not in PERSIST and db not in " ".join(s["infrastructure"]["existing_systems"]): flag("self-managed db on managed host")
    if hk["hosting_type"] == "static" and be != "None": flag("backend on static host")
    if ("auth", "ASP.NET Core Identity") in sup and be != "ASP.NET Core": flag("dotnet auth without dotnet")
    if any(l == "cdn" for l, _ in sup) and s["project"]["platforms"] == ["android"]: flag("cdn for android only")
    if be == "None" and (r["auth"] != "none" or r["payments"]): flag("no backend but auth/payments")
    if "hipaa" in s["compliance"] and any(c in ("Firebase Authentication", "Auth0", "Sentry", "Datadog", "Algolia", "Ably", "Pusher Channels") for _, c in sup): flag("unattested saas under hipaa")
    c = o["estimated_monthly_cost_usd"]
    if o["status"] == "ok" and c["max"] > s["budget"]["monthly_infra_usd"] * 2 + 30: flag("ok but cost >> budget")
    if o["architecture_style"] == "microservices" and not (s["team"]["size"] >= 15): flag("microservices small team")
    if hk["hosting_type"] == "serverless" and r["realtime"]: flag("serverless with realtime")
print("viable", viable, "of", n, "| oracle-violating", bad); print(dict(sus))
for k, v in ex.items():
    print(k, v[:4])
