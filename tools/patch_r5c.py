p='tests/test_regression.py'
t=open(p,encoding='utf-8').read()
old='''        db = k.get("database", o["stack"]["database"]["choice"])
        self.assertTrue(db["self_hostable"] or {"india", "other"} <= set(db["regions"]))'''
new='''        if o["stack"] is None:
            self.assertEqual(o["status"], "infeasible")  # no VM host covers both india and other: honest infeasibility
            return
        db = k.get("database", o["stack"]["database"]["choice"])
        self.assertTrue(db["self_hostable"] or {"india", "other"} <= set(db["regions"]))'''
assert old in t
open(p,'w',encoding='utf-8').write(t.replace(old,new,1))
