p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='''    elif f.eff_res != "none" and not e["self_hostable"]:
        if f.eff_res not in e["regions"] and "global" not in e["regions"]:
            return f"no verified {f.eff_res} region (data_residency={f.eff_res})"'''
new='''    elif f.eff_res != "none" and not e["self_hostable"]:
        for needed in sorted({f.eff_res, f.res} - {"none"}):  # a conflicting pair (e.g. RBI + eu) must satisfy both
            if needed not in e["regions"] and "global" not in e["regions"]:
                return f"no verified {needed} region (data_residency={needed})"'''
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''
    def test_conflicting_rbi_and_residency_keeps_both_constraints(self):
        k = kbmod.load()
        o = run(compliance=["rbi_localisation"], infrastructure__data_residency="other", infrastructure__cloud_preference="none", infrastructure__deployment_model="self_hosted_cloud_vm")
        db = k.get("database", o["stack"]["database"]["choice"])
        self.assertTrue(db["self_hostable"] or {"india", "other"} <= set(db["regions"]))
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
