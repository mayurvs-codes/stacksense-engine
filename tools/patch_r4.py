p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
# strict attestation for SaaS data-handling services under hipaa/pci
rep('''    if K8S.search(e["name"]) and not''','''    strict = [a for a in f.att if a in ("hipaa", "pci_dss")]
    if strict and layer in ("auth", "search", "observability", "realtime", "queue", "cache") and e["saas_only"] and e["cloud"] == "neutral" and not e["compliance"]:
        return f"SaaS vendor without a recorded {'/'.join(strict)} attestation would process regulated data"
    if K8S.search(e["name"]) and not''')
# existing_db: engine upgrade mapping incl. mongodb; keep EOL ones as engine-upgrade
rep('''def existing_db(f, kb):''','''def upgrade_db(f, kb):
    """Database engines already in use whose version is end of life: staying on the same engine (current version) is the lowest-risk upgrade."""
    names = []
    for sysname in f.existing:
        low = sysname.lower()
        if not kbmod.lifecycle_issue(sysname):
            continue
        for pat, name in (("mongodb", "MongoDB Atlas"), ("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("sql server", "Microsoft SQL Server")):
            if pat in low and kb.get("database", name) is not None and name not in names:
                names.append(name)
    return names


def existing_db(f, kb):''')
rep('''    f.reuse = existing_db(f, kb)''','''    f.reuse = existing_db(f, kb)
    f.upgrade = upgrade_db(f, kb)''')
rep('''    nonrel = bool(t & {"document", "kv"})
    if nonrel and not (''','''    nonrel = bool(t & {"document", "kv"})
    if e["name"] in getattr(f, "upgrade", ()):
        s += 1.0  # same engine, current version: smallest migration
        nonrel = False
    if nonrel and not (''')
# hipaa/pci compliance notes
rep('''                         + (", database " + db["name"] if db else "") + "); encrypt''','''                         + (", database " + db["name"] if db else "") + "); confirm every service you use is inside the provider's BAA scope; encrypt''')
open(p,'w',encoding='utf-8').write(s)
g=open('tools/kb_source.py',encoding='utf-8').read()
g=g.replace('add(H, "Cloudflare Pages", regions=("global",), saas=True, htype="static", runtimes=("static",), ws=False, r=(5, 5, 5, 5, 4, 4), ops=1, tags=("static", "free", "cdn"), cap=20_000_000,','add(H, "Cloudflare Pages", regions=("global",), saas=True, htype="static", runtimes=("static",), ws=False, r=(5, 5, 5, 5, 4, 4), ops=1, tags=("static", "free", "cdn"), cap=1_000_000_000,',1)
open('tools/kb_source.py','w',encoding='utf-8').write(g)
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''

class Round4Regressions(unittest.TestCase):
    def test_huge_static_site_uses_a_static_cdn_host(self):
        o = run(project__type="content_site", requirements__auth="none", scale__users_12_months=30_000_000, scale__workload="read_heavy",
                budget__monthly_infra_usd=3000, team__size=3, team__languages=["javascript"])
        self.assertEqual(o["stack"]["hosting"]["choice"], "Cloudflare Pages")
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 100)

    def test_end_of_life_mongodb_is_upgraded_not_abandoned(self):
        o = run(infrastructure__existing_systems=["MongoDB 4.2 cluster"], team__languages=["javascript"], budget__monthly_infra_usd=500)
        self.assertIn("EOL_EXISTING_SYSTEM", {w["code"] for w in o["warnings"]})
        self.assertEqual(o["stack"]["database"]["choice"], "MongoDB Atlas")

    def test_hipaa_excludes_unattested_saas_auth(self):
        o = run(compliance=["hipaa"], requirements__auth="phone_otp", infrastructure__cloud_preference="gcp", infrastructure__data_residency="india")
        self.assertNotIn("Firebase Authentication", sup(o, "auth"))
        self.assertNotIn("Auth0", sup(o, "auth"))

    def test_hipaa_note_tells_you_to_check_baa_scope(self):
        o = run(compliance=["hipaa"])
        self.assertTrue(any("BAA scope" in n for n in o["compliance_notes"]))
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
