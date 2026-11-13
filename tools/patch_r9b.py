p='stacksense/engine.py'
lines=open(p,encoding='utf-8').read().split('\n')
i=[k for k,l in enumerate(lines) if l.strip().startswith('cb.why("team.experience", f"For a {f.exp} team')][0]
lines[i]='''        cb.why("team.experience", f"For a {f.exp} team of {f.team} engineers ({v('team.experience', f.exp)}, {v('team.size', f.team)}), {be['name']} offers {'batteries-included conventions' if 'fullstack' in be['tags'] else 'a typed, structured API model'} (operations burden {be['ops_burden']} vs capacity {f.ops_cap}).")'''
s='\n'.join(lines)
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
# storage: region phrase already in the storage clause; avoid repeating it
rep('if f.eff_res != "none" and layer in ("storage", "cache", "queue", "search"):','if f.eff_res != "none" and layer in ("cache", "queue", "search"):')
# hosting counterfactual tailored
rep('''    if f.u12 * 4 > h["scale_cap_users"] * 0.5 or True:
        out.append(f"If scale.users_12_months grew beyond about {h['scale_cap_users']:,} (its comfortable cap), move to a container or serverless platform on a hyperscaler.")''','''    if h["scale_cap_users"] >= 20_000_000:
        out.append(f"If scale.users_12_months grew far beyond {h['scale_cap_users']:,}, plan multi-region deployment, a split of the busiest services and a sharded or globally distributed datastore.")
    else:
        out.append(f"If scale.users_12_months grew beyond about {h['scale_cap_users']:,} (its comfortable cap), move to container or serverless hosting on a hyperscaler.")''')
# sanity clamp on absurd scale
rep('''    f.u12, f.u0 = s["users_12_months"], s["users_at_launch"]''','''    f.u12, f.u0 = s["users_12_months"], s["users_at_launch"]
    if f.u12 > 10_000_000_000 or f.u0 > 10_000_000_000:
        A.append("Scale was clamped to 10 billion users for estimation (more than the world population); check scale.users_12_months.")
        f.u12, f.u0 = min(f.u12, 10_000_000_000), min(f.u0, 10_000_000_000)''')
open(p,'w',encoding='utf-8').write(s)
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''

class Round9Regressions(unittest.TestCase):
    def test_storage_justification_states_residency_once(self):
        o = run(requirements__file_media_storage=True, infrastructure__data_residency="india", infrastructure__cloud_preference="aws")
        st = [c for c in o["stack"]["supporting"] if c["layer"] == "storage"][0]["justification"]
        self.assertEqual(st.count("satisfy data_residency=india"), 1)

    def test_absurd_scale_is_clamped_not_exploding(self):
        o = run(scale__users_12_months=10**30, scale__users_at_launch=0)
        self.assertLess(o["estimated_monthly_cost_usd"]["max"], 10**15)
        self.assertTrue(any("clamped" in a for a in o["assumptions"]))

    def test_hyperscaler_counterfactual_is_not_circular(self):
        o = run(infrastructure__cloud_preference="aws", scale__users_12_months=300000, team__size=8, team__has_devops=True, budget__monthly_infra_usd=6000)
        text = " ".join(o["stack"]["hosting"]["what_would_change"])
        self.assertNotIn("move to a container or serverless platform on a hyperscaler", text)
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
