p = 'stacksense/engine.py'
s = open(p, encoding='utf-8').read()
old = 'and not (f.rt and f.tier >= 1 and e["name"].startswith("HTMX"))]'
new = 'and not (e["name"].startswith("HTMX") and ((f.rt and f.tier >= 1) or (f.tier >= 3 and f.type != "internal_tool")))]'
assert old in s
open(p, 'w', encoding='utf-8').write(s.replace(old, new, 1))

t = open('tests/test_regression.py', encoding='utf-8').read()
t += '''

class Round10Regressions(unittest.TestCase):
    def test_htmx_not_used_for_public_apps_at_very_high_load(self):
        o = run(project__type="fintech", scale__users_12_months=40_000_000, scale__peak_concurrent_users=900000, team__languages=["java"], team__size=30,
                team__has_devops=True, team__experience="senior", budget__monthly_infra_usd=300000)
        self.assertNotEqual(o["stack"]["frontend"]["choice"], "HTMX with server-rendered templates")

    def test_htmx_still_allowed_for_big_internal_tools(self):
        o = run(project__type="internal_tool", scale__users_12_months=800000, scale__peak_concurrent_users=40000, team__languages=["java"], team__size=6,
                team__has_devops=True, team__experience="senior", budget__monthly_infra_usd=12000)
        self.assertIn(o["stack"]["frontend"]["choice"], ("HTMX with server-rendered templates", "Angular", "Next.js", "React (Vite)", "Nuxt", "SvelteKit", "Blazor", "Astro"))

    def test_maui_chosen_for_csharp_desktop_android_team(self):
        o = run(project__platforms=["desktop", "android"], team__languages=["csharp"], requirements__offline_support=True, project__type="internal_tool", budget__monthly_infra_usd=600)
        self.assertEqual(o["stack"]["frontend"]["choice"], ".NET MAUI")
'''
open('tests/test_regression.py', 'w', encoding='utf-8').write(t)
print('ok')
