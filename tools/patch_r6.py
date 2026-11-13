p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='    if f.avail in ("99.95", "99.99") and host["hosting_type"] == "vm":'
new='    if f.avail in ("99.95", "99.99") and (host["hosting_type"] == "vm" or (host["hosting_type"] == "onprem" and "kubernetes" not in host["tags"])):'
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''
    def test_single_onprem_server_cannot_promise_high_availability(self):
        o = run(infrastructure__deployment_model="on_premise", requirements__availability="99.95", team__size=3, team__experience="senior", team__has_devops=False)
        self.assertIn("SINGLE_VM_AVAILABILITY", {w["code"] for w in o["warnings"]})
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
