import copy
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stacksense import recommend  # noqa: E402


def base():
    return {
        "scenario_id": "T", "project": {"name": "T", "type": "web_app", "platforms": ["web"]},
        "scale": {"users_at_launch": 500, "users_12_months": 5000, "peak_concurrent_users": 100},
        "team": {"size": 3, "experience": "intermediate", "languages": ["python", "typescript"], "has_devops": False},
        "budget": {"monthly_infra_usd": 300}, "timeline": {"mvp_weeks": 8},
        "infrastructure": {"cloud_preference": "any", "deployment_model": "managed_cloud", "data_residency": "none", "existing_systems": []},
        "requirements": {"auth": "email_password", "availability": "99.9"}, "compliance": [],
        "priorities": {"cost": 3, "time_to_market": 3, "scalability": 3, "performance": 3, "maintainability": 3, "security": 3},
    }


def mod(**paths):
    s = base()
    for path, val in paths.items():
        cur = s
        parts = path.split("__")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = val
    return s


def run(**paths):
    return recommend(mod(**paths))


def choices(out):
    st = out["stack"]
    return {k: st[k]["choice"] for k in ("frontend", "backend", "database", "hosting")}


def fuzz(n, seed):
    r = random.Random(seed)
    types = ["content_site", "web_app", "saas_b2b", "ecommerce", "marketplace", "fintech", "healthtech", "internal_tool", "api_platform", "other"]
    out = []
    for i in range(n):
        s = base()
        s["project"]["type"] = r.choice(types)
        s["project"]["platforms"] = r.sample(["web", "android", "ios", "desktop"], r.choice([1, 2]))
        s["scale"]["users_12_months"] = r.choice([100, 3000, 40000, 400000, 4_000_000])
        s["scale"]["users_at_launch"] = s["scale"]["users_12_months"] // 10
        s["team"].update(size=r.choice([1, 3, 6, 10]), experience=r.choice(["beginner", "intermediate", "senior"]), has_devops=r.random() < 0.5,
                         languages=r.sample(["python", "typescript", "java", "csharp", "php", "go"], r.choice([1, 2])))
        s["budget"]["monthly_infra_usd"] = r.choice([0, 50, 300, 3000])
        s["infrastructure"].update(cloud_preference=r.choice(["any", "any", "aws", "gcp", "azure"]),
                                   deployment_model=r.choice(["managed_cloud", "managed_cloud", "self_hosted_cloud_vm", "on_premise"]),
                                   data_residency=r.choice(["none", "india", "eu", "us"]))
        s["requirements"].update(realtime=r.random() < 0.3, file_media_storage=r.random() < 0.4, full_text_search=r.random() < 0.3,
                                 auth=r.choice(["none", "email_password", "social"]), seo_critical=r.random() < 0.3)
        s["compliance"] = r.sample(["gdpr", "dpdp", "iso27001"], r.choice([0, 1]))
        s["scenario_id"] = f"X{i}"
        out.append(s)
    return out
