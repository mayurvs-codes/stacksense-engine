"""Input validation and normalisation for StackSense scenarios (stdlib only).

validate(raw) -> (norm, errors, assumptions)
  norm: fully-populated dict with documented defaults, or None when the input is invalid
  errors: list of {"field": "...", "message": "..."} (every problem is reported, never just the first)
  assumptions: list of strings describing every default or interpretation applied
"""

PROJECT_TYPES = ["content_site", "web_app", "saas_b2b", "ecommerce", "marketplace", "social", "realtime_collab", "fintech",
                 "healthtech", "data_analytics", "iot", "ai_ml_product", "internal_tool", "gaming", "api_platform", "other"]
PLATFORMS = ["web", "android", "ios", "desktop", "api_only"]
TRAFFIC = ["steady", "spiky", "seasonal"]
WORKLOAD = ["read_heavy", "balanced", "write_heavy"]
EXPERIENCE = ["beginner", "intermediate", "senior", "mixed"]
CLOUDS = ["any", "aws", "gcp", "azure", "none"]
DEPLOY = ["managed_cloud", "self_hosted_cloud_vm", "on_premise", "air_gapped"]
RESIDENCY = ["none", "india", "eu", "us", "other"]
AUTH = ["none", "email_password", "social", "phone_otp", "enterprise_sso"]
ML = ["none", "inference_api", "llm_rag", "training"]
AVAIL = ["99", "99.9", "99.95", "99.99"]
COMPLIANCE = ["gdpr", "dpdp", "hipaa", "pci_dss", "rbi_localisation", "soc2", "iso27001"]
PRIORITY_KEYS = ["cost", "time_to_market", "scalability", "performance", "maintainability", "security"]
BOOLS = ["realtime", "offline_support", "full_text_search", "file_media_storage", "payments", "multi_tenant", "seo_critical"]

GEO = ["single_region", "regional", "global"]
TOLERANCE = ["low", "medium", "high"]
SENSITIVITY = ["public", "internal", "confidential", "restricted"]
SYNC = ["last_write_wins", "merge", "strict_consistency"]
INTEGRATIONS_KNOWN = ["erp", "crm", "payments_gateway", "sms", "email", "accounting", "analytics", "identity", "legacy_db"]


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool) or (isinstance(v, float) and v.is_integer())


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and v not in (float("inf"), float("-inf"))


def _fmt(v):
    return "true" if v is True else "false" if v is False else str(v)


class _Ctx:
    def __init__(self, raw):
        self.raw, self.errors, self.assumptions, self.out = raw, [], [], {}

    def err(self, field, msg):
        self.errors.append({"field": field, "message": msg})

    def section(self, name, required):
        sec = self.raw.get(name)
        if sec is None and name in self.raw:
            self.err(name, f"'{name}' must be an object, got null")
            return {}
        if sec is None:
            return {}
        if not isinstance(sec, dict):
            self.err(name, f"'{name}' must be an object")
            return {}
        return sec

    def get(self, sec, secname, key, kind, required, default, allowed=None, minimum=None, maximum=None, exclusive_min=None, note=None):
        path = f"{secname}.{key}"
        present = key in sec and sec[key] is not None if kind != "nullable_int" else key in sec
        val = sec.get(key)
        if not present or (val is None and kind != "nullable_int"):
            if required:
                self.err(path, f"required field '{path}' is missing")
                return None
            self.assumptions.append(f"Default applied: {path} = {_fmt(default)}" + (f" ({note})" if note else ""))
            return default
        ok = True
        if kind == "string":
            ok = isinstance(val, str)
        elif kind == "int":
            ok = _is_int(val)
        elif kind == "num":
            ok = _is_num(val)
        elif kind == "bool":
            ok = isinstance(val, bool)
        elif kind == "nullable_int":
            if val is None:
                self.assumptions.append(f"Default applied: {path} = null (no latency target assumed)")
                return None
            ok = _is_int(val)
        elif kind == "enum":
            ok = isinstance(val, str) and val in allowed
        elif kind == "enum_list":
            ok = isinstance(val, list) and all(isinstance(x, str) and x in allowed for x in val)
        elif kind == "str_list":
            ok = isinstance(val, list) and all(isinstance(x, str) for x in val)
        if not ok:
            exp = {"int": "an integer", "num": "a number", "bool": "true or false", "string": "a string", "str_list": "a list of strings",
                   "nullable_int": "an integer or null"}.get(kind) or (f"one of {allowed}" if kind == "enum" else f"a list whose items are in {allowed}")
            self.err(path, f"'{path}' must be {exp}, got {val!r}")
            return None
        if kind in ("int", "num", "nullable_int"):
            if minimum is not None and val < minimum:
                self.err(path, f"'{path}' must be >= {minimum}, got {val}")
                return None
            if exclusive_min is not None and val <= exclusive_min:
                self.err(path, f"'{path}' must be > {exclusive_min}, got {val}")
                return None
            if maximum is not None and val > maximum:
                self.err(path, f"'{path}' must be <= {maximum}, got {val}")
                return None
            if kind in ("int", "nullable_int") and isinstance(val, float):
                val = int(val)
        if kind == "enum_list" and len(set(val)) != len(val):
            val = sorted(set(val), key=val.index)
        return val


def validate(raw):
    if not isinstance(raw, dict):
        return None, [{"field": "$", "message": "scenario must be a JSON object"}], []
    c = _Ctx(raw)
    n = {}
    known = {"scenario_id", "project", "scale", "team", "budget", "timeline", "infrastructure", "requirements", "compliance", "priorities", "extra"}
    for k in sorted(raw):
        if k not in known:
            c.assumptions.append(f"Ignored unknown top-level field '{k}'")
    p = c.section("project", True)
    n["project"] = {
        "name": c.get(p, "project", "name", "string", False, ""),
        "type": c.get(p, "project", "type", "enum", True, None, PROJECT_TYPES),
        "description": c.get(p, "project", "description", "string", False, ""),
        "platforms": c.get(p, "project", "platforms", "enum_list", True, None, PLATFORMS),
    }
    if isinstance(n["project"]["platforms"], list) and not n["project"]["platforms"]:
        c.err("project.platforms", "'project.platforms' must be a non-empty list")
    elif isinstance(n["project"]["platforms"], list):
        n["project"]["platforms"] = sorted(set(n["project"]["platforms"]), key=PLATFORMS.index)  # order is irrelevant: canonicalise
    s = c.section("scale", True)
    n["scale"] = {
        "users_at_launch": c.get(s, "scale", "users_at_launch", "int", True, None, minimum=0),
        "users_12_months": c.get(s, "scale", "users_12_months", "int", True, None, minimum=0),
        "peak_concurrent_users": c.get(s, "scale", "peak_concurrent_users", "int", False, None, minimum=0, note="estimated later as 10% of users_12_months"),
        "traffic_pattern": c.get(s, "scale", "traffic_pattern", "enum", False, "steady", TRAFFIC),
        "workload": c.get(s, "scale", "workload", "enum", False, "balanced", WORKLOAD),
        "data_volume_gb_12_months": c.get(s, "scale", "data_volume_gb_12_months", "num", False, 10, minimum=0, note="small dataset assumed"),
    }
    t = c.section("team", True)
    n["team"] = {
        "size": c.get(t, "team", "size", "int", True, None, minimum=1),
        "experience": c.get(t, "team", "experience", "enum", True, None, EXPERIENCE),
        "languages": None, "has_devops": c.get(t, "team", "has_devops", "bool", False, False),
    }
    langs = t.get("languages") if t else None
    if "languages" not in t or langs is None:
        c.err("team.languages", "required field 'team.languages' is missing (an empty list is allowed)")
    elif not isinstance(langs, list) or not all(isinstance(x, str) for x in langs):
        c.err("team.languages", f"'team.languages' must be a list of strings, got {langs!r}")
    else:
        n["team"]["languages"] = sorted(set(x.strip().lower() for x in langs))
    b = c.section("budget", True)
    n["budget"] = {"monthly_infra_usd": c.get(b, "budget", "monthly_infra_usd", "num", True, None, minimum=0)}
    tl = c.section("timeline", True)
    n["timeline"] = {"mvp_weeks": c.get(tl, "timeline", "mvp_weeks", "int", True, None, minimum=1)}
    i = c.section("infrastructure", False)
    n["infrastructure"] = {
        "cloud_preference": c.get(i, "infrastructure", "cloud_preference", "enum", False, "any", CLOUDS),
        "deployment_model": c.get(i, "infrastructure", "deployment_model", "enum", False, "managed_cloud", DEPLOY),
        "data_residency": c.get(i, "infrastructure", "data_residency", "enum", False, "none", RESIDENCY),
        "existing_systems": c.get(i, "infrastructure", "existing_systems", "str_list", False, []),
    }
    if isinstance(n["infrastructure"]["existing_systems"], list):
        n["infrastructure"]["existing_systems"] = sorted(set(n["infrastructure"]["existing_systems"]))
    r = c.section("requirements", False)
    rq = {k: c.get(r, "requirements", k, "bool", False, False) for k in BOOLS}
    rq["auth"] = c.get(r, "requirements", "auth", "enum", False, "none", AUTH)
    rq["ml_features"] = c.get(r, "requirements", "ml_features", "enum", False, "none", ML)
    rq["availability"] = c.get(r, "requirements", "availability", "enum", False, "99.9", AVAIL)
    rq["p95_latency_ms"] = c.get(r, "requirements", "p95_latency_ms", "nullable_int", False, None, exclusive_min=0)
    n["requirements"] = rq
    comp = raw.get("compliance", "__missing__")
    if comp == "__missing__" or comp is None:
        n["compliance"] = []
        c.assumptions.append("Default applied: compliance = []")
    elif not isinstance(comp, list) or not all(isinstance(x, str) and x in COMPLIANCE for x in comp):
        c.err("compliance", f"'compliance' must be a list whose items are in {COMPLIANCE}, got {comp!r}")
    else:
        n["compliance"] = sorted(set(comp), key=COMPLIANCE.index)
    pr = c.section("priorities", False)
    if not pr:
        c.assumptions.append("Default applied: priorities (cost, time_to_market, scalability, performance, maintainability, security) = 3 each")
    prio = {}
    for k in PRIORITY_KEYS:
        v = pr.get(k) if pr else None
        if v is None:
            prio[k] = 3
            if pr:
                c.assumptions.append(f"Default applied: priorities.{k} = 3")
        elif not _is_int(v) or not 1 <= v <= 5:
            c.err(f"priorities.{k}", f"'priorities.{k}' must be an integer from 1 to 5, got {v!r}")
        else:
            prio[k] = int(v)
    for k in sorted(pr or {}):
        if k not in PRIORITY_KEYS:
            c.assumptions.append(f"Ignored unknown priority key 'priorities.{k}'")
    n["priorities"] = prio
    ex = raw.get("extra")
    n["extra"] = {}
    if ex is not None and not isinstance(ex, dict):
        c.err("extra", "'extra' must be an object")
    elif isinstance(ex, dict):
        _extras(c, ex, n["extra"])
    if c.errors:
        return None, c.errors, c.assumptions
    return n, [], c.assumptions


def _extras(c, ex, out):
    specs = {
        "expected_rps": ("num", None), "geo_distribution": ("enum", GEO), "vendor_lock_in_tolerance": ("enum", TOLERANCE),
        "existing_licences": ("str_list", None), "hiring_plan_6m": ("int", None), "data_sensitivity": ("enum", SENSITIVITY),
        "integration_needs": ("str_list", None), "sync_conflict_tolerance": ("enum", SYNC),
    }
    for k in sorted(ex):
        v = ex[k]
        path = f"extra.{k}"
        if k not in specs:
            c.assumptions.append(f"Ignored unknown extra parameter '{path}'")
            continue
        kind, allowed = specs[k]
        if v is None:
            continue
        ok = ((kind == "num" and _is_num(v) and v >= 0) or (kind == "int" and _is_int(v) and v >= 0) or
              (kind == "enum" and isinstance(v, str) and v in allowed) or
              (kind == "str_list" and isinstance(v, list) and all(isinstance(x, str) for x in v)))
        if not ok:
            c.err(path, f"'{path}' has an invalid value {v!r}" + (f"; allowed: {allowed}" if allowed else ""))
        else:
            out[k] = [x.strip().lower() for x in v] if kind == "str_list" and k == "integration_needs" else v
    for k in ("geo_distribution", "vendor_lock_in_tolerance", "data_sensitivity", "sync_conflict_tolerance"):
        if k not in out and k in specs:
            pass
