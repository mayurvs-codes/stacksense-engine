g=open('tools/kb_source.py',encoding='utf-8').read()
old='sup("search", "Algolia"'
new='''sup("search", "Pagefind", self_host=True, r=(5, 5, 3, 5, 4, 4), ops=1, tags=("search", "client_only", "static_search"), cost=((0, 0), (0, 0)), cap=2_000_000,
    strengths=("Static client-side search index built at deploy time: no search server to run, works on any static host",), limits=("Index lives in the browser: suits documentation and content sites, not large or access-controlled datasets",),
    src=[("https://pagefind.app/", "Pagefind")])
sup("search", "Algolia"'''
assert old in g
g=g.replace(old,new,1)
open('tools/kb_source.py','w',encoding='utf-8').write(g)
a=open('tools/gen_kb_audit.py',encoding='utf-8').read()
a=a.replace('"SeaweedFS": "seaweedfs/seaweedfs"}','"SeaweedFS": "seaweedfs/seaweedfs", "Pagefind": "CloudCannon/pagefind", "PyTorch": "pytorch/pytorch"}',1)
open('tools/gen_kb_audit.py','w',encoding='utf-8').write(a)
p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
rep('def compat_support(e, layer, role, f, be, fe, db):','def compat_support(e, layer, role, f, be, fe, db, host=None):')
rep('''    t = set(e["tags"])
    if "library" in t and e["languages"]:''','''    t = set(e["tags"])
    if "client_only" in t and be is not None:
        return False  # client-side search only makes sense for backend-less sites
    if host is not None and host["hosting_type"] == "static" and e["self_hostable"] and not e["saas_only"] and not t & {"library", "client_only"}:
        return False  # a static host cannot run a server component
    if "library" in t and e["languages"]:''')
rep('compat_support(e, layer, role, f, be, fe, db)]','compat_support(e, layer, role, f, be, fe, db, host)]')
open(p,'w',encoding='utf-8').write(s)
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''

class Round8Regressions(unittest.TestCase):
    def test_static_host_never_gets_a_search_server(self):
        o = run(project__type="content_site", requirements__auth="none", requirements__full_text_search=True, budget__monthly_infra_usd=0,
                team__size=1, team__experience="beginner", team__languages=["javascript"], scale__users_12_months=3000)
        self.assertEqual(sup(o, "search"), ["Pagefind"])
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 25)

    def test_client_side_search_not_used_with_a_backend(self):
        o = run(requirements__full_text_search=True, scale__users_12_months=200000, budget__monthly_infra_usd=3000)
        self.assertNotIn("Pagefind", sup(o, "search"))
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
