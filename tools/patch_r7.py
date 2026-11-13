p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
# content site search does not force a backend
rep('f.dynamic = bool(f.auth != "none" or f.pay or f.rt or f.ml != "none" or f.files or f.mt or f.offline or f.fts or f.type in DYNAMIC_TYPES or f.type == "other" and f.u12 > 0 and False)',
    'f.dynamic = bool(f.auth != "none" or f.pay or f.rt or f.ml != "none" or f.files or f.mt or f.offline or (f.fts and f.type != "content_site") or f.type in DYNAMIC_TYPES)')
# proprietary penalty
rep('''        if "proprietary" in e["tags"]:
            p += 1.2''','''        if "proprietary" in e["tags"]:
            p += 1.8''')
# HTMX realtime exclusion
rep('''    if fe["name"].startswith("HTMX"):
        return be is not None''','''    if fe["name"].startswith("HTMX"):
        return be is not None''')
rep('''        cands = [e for e in kb.layer("frontend") if host_ok_for_frontend(host, e, be)]''','''        cands = [e for e in kb.layer("frontend") if host_ok_for_frontend(host, e, be) and not (f.rt and f.tier >= 1 and e["name"].startswith("HTMX"))]''')
open(p,'w',encoding='utf-8').write(s)
g=open('tools/kb_source.py',encoding='utf-8').read()
g=g.replace('"Google Cloud Pub/Sub", "Amazon SQS", "Azure Service Bus",','"Google Cloud Pub/Sub", "Amazon SQS", "Azure Service Bus", "Microsoft Entra ID",',1)
open('tools/kb_source.py','w',encoding='utf-8').write(g)
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''

class Round7Regressions(unittest.TestCase):
    def test_docs_site_with_search_stays_static(self):
        o = run(project__type="content_site", requirements__auth="none", requirements__full_text_search=True, scale__users_12_months=3000,
                infrastructure__deployment_model="on_premise", team__languages=["python"], team__size=2, budget__monthly_infra_usd=50)
        self.assertEqual(o["stack"]["backend"]["choice"], "None")
        self.assertEqual(o["architecture_style"], "static")
        self.assertTrue(sup(o, "search"))

    def test_htmx_not_used_for_realtime_beyond_tiny_scale(self):
        o = run(requirements__realtime=True, team__languages=["java"], scale__users_12_months=120000, scale__peak_concurrent_users=5000, budget__monthly_infra_usd=4000)
        self.assertNotEqual(o["stack"]["frontend"]["choice"], "HTMX with server-rendered templates")

    def test_low_lock_in_prefers_open_identity(self):
        o = run(extra=None) if False else None
        raw = mod(requirements__auth="social", infrastructure__cloud_preference="aws", infrastructure__deployment_model="self_hosted_cloud_vm", team__size=5, team__has_devops=True, budget__monthly_infra_usd=2000, scale__users_12_months=40000)
        raw["extra"] = {"vendor_lock_in_tolerance": "low"}
        self.assertEqual(sup(recommend(raw), "auth"), ["Keycloak"])
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
