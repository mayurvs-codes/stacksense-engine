"""Round 8: modified versions of the public scenarios (what the judges said they would test) plus a few new ones."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = {s["scenario_id"]: s for s in json.loads((ROOT / "data/scenarios/public_scenarios.json").read_text(encoding="utf-8"))}


def M(base_id, new_id, cls, **mods):
    s = copy.deepcopy(PUB[base_id])
    s["scenario_id"] = new_id
    s["_class"] = cls
    for path, val in mods.items():
        cur = s
        parts = path.split("__")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = val
    return s


def build8():
    L = []
    L.append(M("P1", "R8-01", "P1_budget_up", budget__monthly_infra_usd=200, requirements__auth="email_password", team__languages=["python"]))
    L.append(M("P1", "R8-02", "P1_eu_gdpr", infrastructure__data_residency="eu", compliance=["gdpr"], requirements__full_text_search=True))
    L.append(M("P2", "R8-03", "P2_budget_x10", budget__monthly_infra_usd=1500, scale__users_12_months=300000, scale__peak_concurrent_users=8000))
    L.append(M("P2", "R8-04", "P2_no_residency", infrastructure__data_residency="none", compliance=[], requirements__auth="social"))
    L.append(M("P2", "R8-05", "P2_aws_pinned", infrastructure__cloud_preference="aws", team__languages=["java"]))
    L.append(M("P3", "R8-06", "P3_india", infrastructure__data_residency="india", compliance=["dpdp"], requirements__payments=True))
    L.append(M("P3", "R8-07", "P3_small_team", team__size=2, team__has_devops=False, team__experience="intermediate", budget__monthly_infra_usd=300))
    L.append(M("P4", "R8-08", "P4_azure", infrastructure__cloud_preference="azure", team__languages=["csharp"]))
    L.append(M("P4", "R8-09", "P4_no_rbi", compliance=["pci_dss", "dpdp"], infrastructure__data_residency="none", infrastructure__cloud_preference="any"))
    L.append(M("P4", "R8-10", "P4_cheap", budget__monthly_infra_usd=400, team__size=2, team__experience="intermediate", team__has_devops=False))
    L.append(M("P5", "R8-11", "P5_gcp_pref", infrastructure__cloud_preference="gcp", infrastructure__existing_systems=["On-prem SQL Server 2014", "Microsoft Entra ID (Azure AD)"]))
    L.append(M("P5", "R8-12", "P5_onprem", infrastructure__deployment_model="on_premise", infrastructure__cloud_preference="any"))
    L.append(M("P6", "R8-13", "P6_online_only", requirements__offline_support=False, requirements__auth="email_password"))
    L.append(M("P6", "R8-14", "P6_ios_added", project__platforms=["android", "ios"], budget__monthly_infra_usd=250))
    L.append(M("P6", "R8-15", "P6_strict", extra={"sync_conflict_tolerance": "strict_consistency"}, compliance=["dpdp", "iso27001"]))
    return L
