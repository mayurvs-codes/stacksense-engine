"""Adversarial review helper: writes review/round_N/scenarios.json (hand-designed, NOT taken from the public set), runs the engine on each,
runs the independent gate oracle on every output and writes review/round_N/summary.md for a human/skeptical critique.
Usage: python tools/review_round.py 1"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gate"))
import oracle  # noqa: E402  (read-only use of the independent oracle)
from stacksense import recommend  # noqa: E402


def B():
    return {
        "scenario_id": "", "project": {"name": "", "type": "web_app", "description": "", "platforms": ["web"]},
        "scale": {"traffic_pattern": "steady", "workload": "balanced", "users_at_launch": 1000, "users_12_months": 20000, "peak_concurrent_users": 500, "data_volume_gb_12_months": 40},
        "team": {"has_devops": False, "size": 4, "experience": "intermediate", "languages": ["python", "typescript"]},
        "budget": {"monthly_infra_usd": 500}, "timeline": {"mvp_weeks": 12},
        "infrastructure": {"cloud_preference": "any", "deployment_model": "managed_cloud", "data_residency": "none", "existing_systems": []},
        "requirements": {"realtime": False, "offline_support": False, "full_text_search": False, "file_media_storage": False, "payments": False, "auth": "email_password",
                         "multi_tenant": False, "ml_features": "none", "seo_critical": False, "availability": "99.9", "p95_latency_ms": None},
        "compliance": [], "priorities": {"cost": 3, "time_to_market": 3, "scalability": 3, "performance": 3, "maintainability": 3, "security": 3},
    }


def S(sid, cls, **mods):
    s = B()
    s["scenario_id"] = sid
    s["_class"] = cls
    for path, val in mods.items():
        cur = s
        parts = path.split("__")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = val
    return s


def build():
    L = []
    L.append(S("R1-01", "invalid", project__type="blockchain", team__size=0))
    L.append(S("R1-02", "invalid", scale__users_12_months="many", budget__monthly_infra_usd=-10, priorities__cost=7))
    inv = B(); inv["scenario_id"] = "R1-03"; inv["_class"] = "invalid"; del inv["team"]["languages"]; inv["infrastructure"]["deployment_model"] = "mainframe"; L.append(inv)
    L.append(S("R1-04", "contradiction", scale__users_12_months=20_000_000, scale__users_at_launch=2_000_000, budget__monthly_infra_usd=200, team__size=2))
    L.append(S("R1-05", "contradiction", requirements__availability="99.99", team__size=1, team__experience="beginner", budget__monthly_infra_usd=30))
    L.append(S("R1-06", "contradiction", timeline__mvp_weeks=1, project__platforms=["web", "android", "ios", "desktop"], team__size=1))
    L.append(S("R1-07", "overengineering", project__type="content_site", scale__users_12_months=8_000_000, scale__workload="read_heavy", requirements__auth="none", team__size=1,
               team__languages=["javascript"], budget__monthly_infra_usd=100, requirements__seo_critical=True))
    L.append(S("R1-08", "overengineering", project__type="internal_tool", scale__users_12_months=60, scale__users_at_launch=60, scale__peak_concurrent_users=10, team__size=1, budget__monthly_infra_usd=40,
               team__languages=["python"], requirements__auth="enterprise_sso"))
    L.append(S("R1-09", "overengineering", project__type="saas_b2b", scale__users_12_months=400, team__size=2, team__experience="beginner", requirements__multi_tenant=True, budget__monthly_infra_usd=60))
    L.append(S("R1-10", "regulated", project__type="healthtech", compliance=["hipaa", "gdpr"], infrastructure__data_residency="eu", requirements__file_media_storage=True, team__experience="senior", team__has_devops=True, team__size=6, budget__monthly_infra_usd=2500))
    L.append(S("R1-11", "regulated", project__type="fintech", compliance=["pci_dss", "rbi_localisation", "dpdp"], requirements__payments=True, infrastructure__data_residency="india", infrastructure__cloud_preference="azure", team__languages=["csharp"], budget__monthly_infra_usd=4000, team__size=7, team__has_devops=True, team__experience="senior"))
    L.append(S("R1-12", "regulated", project__type="ecommerce", compliance=["pci_dss", "gdpr"], requirements__payments=True, infrastructure__data_residency="eu", requirements__full_text_search=True, requirements__seo_critical=True, budget__monthly_infra_usd=800))
    L.append(S("R1-13", "regulated", project__type="social", compliance=["dpdp"], infrastructure__data_residency="india", requirements__auth="phone_otp", requirements__file_media_storage=True, scale__users_12_months=900000, budget__monthly_infra_usd=6000, team__size=9, team__has_devops=True, team__experience="senior"))
    L.append(S("R1-14", "legacy", infrastructure__existing_systems=["Python 2.7 Django monolith", "MySQL 5.7 database", "AngularJS 1.x frontend"], team__languages=["python"], budget__monthly_infra_usd=900))
    L.append(S("R1-15", "legacy", infrastructure__existing_systems=["SQL Server 2012", "Windows Server 2012 R2"], team__languages=["csharp", "sql"], infrastructure__cloud_preference="azure", project__type="internal_tool"))
    L.append(S("R1-16", "restricted", infrastructure__deployment_model="air_gapped", project__type="internal_tool", team__size=3, requirements__auth="enterprise_sso", requirements__file_media_storage=True, requirements__full_text_search=True, budget__monthly_infra_usd=1000))
    L.append(S("R1-17", "restricted", infrastructure__deployment_model="on_premise", team__size=6, team__has_devops=True, team__experience="senior", requirements__realtime=True, scale__users_12_months=200000, budget__monthly_infra_usd=3000))
    L.append(S("R1-18", "restricted", infrastructure__deployment_model="self_hosted_cloud_vm", infrastructure__cloud_preference="aws", requirements__realtime=False, requirements__payments=True, budget__monthly_infra_usd=700))
    L.append(S("R1-19", "skill", team__languages=["rust"], budget__monthly_infra_usd=400, project__type="api_platform", project__platforms=["api_only"]))
    L.append(S("R1-20", "skill", team__languages=["cobol", "fortran"], project__type="web_app"))
    L.append(S("R1-21", "offline", project__type="other", project__platforms=["android"], requirements__offline_support=True, requirements__auth="phone_otp", requirements__file_media_storage=True, infrastructure__data_residency="india", budget__monthly_infra_usd=120, team__size=2, team__languages=["kotlin"]))
    L.append(S("R1-22", "offline", project__type="internal_tool", project__platforms=["android", "ios"], requirements__offline_support=True, infrastructure__deployment_model="on_premise", team__languages=["java"], team__size=5, team__has_devops=True))
    L.append(S("R1-23", "realtime_scale", project__type="gaming", requirements__realtime=True, scale__users_12_months=3_000_000, scale__peak_concurrent_users=200000, scale__traffic_pattern="spiky", team__size=12, team__has_devops=True, team__experience="senior", team__languages=["go", "typescript"], budget__monthly_infra_usd=30000, requirements__p95_latency_ms=60))
    L.append(S("R1-24", "realtime_scale", project__type="realtime_collab", requirements__realtime=True, scale__peak_concurrent_users=2000, team__languages=["typescript"], budget__monthly_infra_usd=400, requirements__p95_latency_ms=120))
    L.append(S("R1-25", "ml", project__type="ai_ml_product", requirements__ml_features="llm_rag", requirements__full_text_search=True, team__languages=["python"], budget__monthly_infra_usd=1500, infrastructure__cloud_preference="gcp"))
    L.append(S("R1-26", "ml", project__type="ai_ml_product", requirements__ml_features="training", infrastructure__deployment_model="on_premise", team__languages=["python"], team__size=4, team__has_devops=True, budget__monthly_infra_usd=2000))
    L.append(S("R1-27", "extreme_budget", budget__monthly_infra_usd=0, project__type="web_app", team__size=1, team__experience="beginner", team__languages=["javascript"], scale__users_12_months=500))
    L.append(S("R1-28", "extreme_budget", budget__monthly_infra_usd=250000, scale__users_12_months=40_000_000, scale__users_at_launch=4_000_000, scale__peak_concurrent_users=900000, team__size=40, team__has_devops=True, team__experience="senior", team__languages=["java", "go", "typescript"], requirements__realtime=True, requirements__payments=True, requirements__availability="99.99"))
    mini = {"scenario_id": "R1-29", "_class": "minimal", "project": {"type": "ecommerce", "platforms": ["web"]}, "scale": {"users_at_launch": 100, "users_12_months": 1000},
            "team": {"size": 2, "experience": "beginner", "languages": ["php"]}, "budget": {"monthly_infra_usd": 80}, "timeline": {"mvp_weeks": 6}}
    L.append(mini)
    mini2 = {"scenario_id": "R1-30", "_class": "minimal", "project": {"type": "data_analytics", "platforms": ["web"]}, "scale": {"users_at_launch": 20, "users_12_months": 200},
             "team": {"size": 5, "experience": "senior", "languages": []}, "budget": {"monthly_infra_usd": 5000}, "timeline": {"mvp_weeks": 20}}
    L.append(mini2)
    ex1 = S("R1-31", "extras", project__type="marketplace", extra={"expected_rps": 4000, "geo_distribution": "global", "vendor_lock_in_tolerance": "low", "data_sensitivity": "confidential", "integration_needs": ["erp", "sms"], "hiring_plan_6m": 4}, budget__monthly_infra_usd=3000, requirements__payments=True, requirements__file_media_storage=True, scale__users_12_months=300000)
    L.append(ex1)
    ex2 = S("R1-32", "extras", project__type="iot", extra={"existing_licences": ["Microsoft 365 E5", "Oracle Database Enterprise"], "sync_conflict_tolerance": "strict_consistency", "data_sensitivity": "restricted"}, requirements__offline_support=True, project__platforms=["android"], budget__monthly_infra_usd=1200)
    L.append(ex2)
    return L


def main():
    n = sys.argv[1] if len(sys.argv) > 1 else "1"
    d = ROOT / "review" / f"round_{n}"
    d.mkdir(parents=True, exist_ok=True)
    scns = build()
    (d / "scenarios.json").write_text(json.dumps(scns, indent=1), encoding="utf-8")
    kb = oracle.load_kb()
    rows, bad = [], 0
    for s in scns:
        raw = {k: v for k, v in s.items() if k != "_class"}
        o = recommend(raw)
        viol = oracle.violations(raw, o, kb) if o["status"] != "invalid_input" else []
        bad += bool(viol)
        st = o["stack"]
        if st:
            core = " | ".join(f"{k[:2]}={st[k]['choice']}" for k in ("frontend", "backend", "database", "hosting"))
            sup = ", ".join(f"{c['layer']}:{c['choice']}" for c in st["supporting"])
        else:
            core = sup = "-"
        rows.append(f"### {s['scenario_id']} [{s['_class']}] status={o['status']} style={o['architecture_style']} cost=${o['estimated_monthly_cost_usd']['min']}-{o['estimated_monthly_cost_usd']['max']}\n"
                    f"- stack: {core}\n- supporting: {sup}\n- warnings: {[w['code'] + ':' + w['severity'] for w in o['warnings']]}\n"
                    f"- errors: {[e['field'] for e in o['validation_errors']]}\n- oracle violations: {viol}\n")
    (d / "summary.md").write_text("# Round %s engine outputs (auto-generated)\n\n%d scenarios, %d with oracle violations\n\n" % (n, len(scns), bad) + "\n".join(rows), encoding="utf-8")
    print(len(scns), "scenarios,", bad, "with oracle violations")


if __name__ == "__main__":
    main()
