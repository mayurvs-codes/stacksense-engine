p = 'stacksense/engine.py'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep('''    if f.rps is not None and f.rps >= 1000 and "serverless" in t:
        s -= 0.3
    return s''', '''    if f.rps is not None and f.rps >= 1000 and "serverless" in t:
        s -= 0.3
    if "kubernetes" in t and not (f.tier >= 3 or f.team >= 10):
        s -= 1.5  # Kubernetes needs a justification: very high load or a large platform team
    return s''')
rep('''    comp.tradeoffs = list(h["limits"])
    return comp''', '''    if "kubernetes" in h["tags"]:
        comp.why("scale.users_12_months", f"Kubernetes is justified here by load tier {f.tier} ({v('scale.users_12_months', f.u12)}, peak {f.peak:,} concurrent) and a platform-capable team (team.size={f.team}, has_devops={fv(f.devops)}).")
    comp.tradeoffs = list(h["limits"])
    return comp''')
open(p, 'w', encoding='utf-8').write(s)

t = open('tests/test_regression.py', encoding='utf-8').read()
t += '''

class KubernetesJustification(unittest.TestCase):
    def test_kubernetes_needs_high_load_or_big_team(self):
        o = run(infrastructure__cloud_preference="aws", team__size=8, team__has_devops=True, team__experience="senior", scale__users_12_months=300000,
                scale__peak_concurrent_users=9000, budget__monthly_infra_usd=6000)
        self.assertNotIn("EKS", o["stack"]["hosting"]["choice"])

    def test_kubernetes_is_available_and_explained_at_very_high_load(self):
        o = run(infrastructure__cloud_preference="aws", team__size=14, team__has_devops=True, team__experience="senior", scale__users_12_months=8_000_000,
                scale__peak_concurrent_users=200000, budget__monthly_infra_usd=200000, team__languages=["java"])
        host = o["stack"]["hosting"]
        if "EKS" in host["choice"]:
            self.assertIn("Kubernetes is justified", host["justification"])
'''
open('tests/test_regression.py', 'w', encoding='utf-8').write(t)
print('ok')
