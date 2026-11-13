import json
import unittest

from tests.helpers import base, choices, mod, run
from stacksense import recommend, kb as kbmod


def codes(out):
    return {w["code"] for w in out["warnings"]}


class EngineTests(unittest.TestCase):
    def test_output_has_all_top_level_fields(self):
        o = run()
        for k in ("status", "summary", "architecture_style", "stack", "estimated_monthly_cost_usd", "warnings", "assumptions", "validation_errors", "engine_version"):
            self.assertIn(k, o)

    def test_deterministic_same_input_same_bytes(self):
        a = json.dumps(run(), sort_keys=True)
        b = json.dumps(run(), sort_keys=True)
        self.assertEqual(a, b)

    def test_scenario_id_and_name_do_not_change_stack(self):
        a = choices(run())
        other = mod()
        other["scenario_id"] = "other"
        other["project"]["name"] = "Zzz"
        other["project"]["description"] = "anything at all"
        self.assertEqual(a, choices(recommend(other)))

    def test_description_never_changes_stack(self):
        a = choices(run(project__description=""))
        b = choices(run(project__description="a huge multiplayer game with ML and payments"))
        self.assertEqual(a, b)

    def test_list_order_does_not_matter(self):
        a = choices(run(team__languages=["python", "typescript"]))
        b = choices(run(team__languages=["typescript", "python"]))
        self.assertEqual(a, b)

    def test_invalid_input_has_null_stack(self):
        o = run(project__type="nope")
        self.assertEqual(o["status"], "invalid_input")
        self.assertIsNone(o["stack"])
        self.assertTrue(o["validation_errors"])

    def test_content_site_is_static_without_backend(self):
        o = run(project__type="content_site", requirements__auth="none", team__languages=["javascript"], budget__monthly_infra_usd=0,
                team__size=1, team__experience="beginner")
        self.assertEqual(o["architecture_style"], "static")
        self.assertEqual(o["stack"]["backend"]["choice"], "None")
        self.assertEqual(o["stack"]["database"]["choice"], "None")
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 25)

    def test_tiny_team_never_gets_microservices_or_kubernetes(self):
        o = run(team__size=2, scale__users_12_months=100000)
        self.assertNotEqual(o["architecture_style"], "microservices")
        names = [o["stack"][k]["choice"] for k in ("frontend", "backend", "database", "hosting")] + [c["choice"] for c in o["stack"]["supporting"]]
        self.assertFalse([n for n in names if "ubernetes" in n or "k3s" in n])

    def test_backend_matches_team_language(self):
        self.assertEqual(run(team__languages=["csharp"])["stack"]["backend"]["choice"], "ASP.NET Core")
        self.assertEqual(run(team__languages=["php"])["stack"]["backend"]["choice"], "Laravel")

    def test_unknown_language_yields_skill_warning(self):
        o = run(team__languages=["cobol"])
        self.assertIn("SKILL_MISMATCH", codes(o))
        self.assertNotEqual(o["status"], "ok")

    def test_cloud_preference_is_hard(self):
        for cloud, words in (("aws", ("AWS", "Amazon")), ("azure", ("Azure",)), ("gcp", ("Google",))):
            o = run(infrastructure__cloud_preference=cloud)
            host = o["stack"]["hosting"]["choice"]
            self.assertTrue(any(w in host for w in words), host)

    def test_air_gapped_has_only_self_hostable(self):
        o = run(infrastructure__deployment_model="air_gapped", requirements__realtime=False)
        k = kbmod.load()
        for layer in ("hosting", "database"):
            e = k.get(layer, o["stack"][layer]["choice"])
            self.assertTrue(e["self_hostable"] and not e["saas_only"], layer)
        self.assertFalse(any(c["layer"] == "cdn" for c in o["stack"]["supporting"]))

    def test_air_gapped_payments_is_flagged(self):
        o = run(infrastructure__deployment_model="air_gapped", requirements__payments=True)
        self.assertIn("AIRGAP_PAYMENTS", codes(o))
        self.assertNotEqual(o["status"], "ok")

    def test_on_premise_payments_is_infeasible(self):
        o = run(infrastructure__deployment_model="on_premise", requirements__payments=True)
        self.assertEqual(o["status"], "infeasible")
        self.assertIsNone(o["stack"])

    def test_india_residency_uses_india_capable_hosting(self):
        o = run(infrastructure__data_residency="india")
        h = kbmod.load().get("hosting", o["stack"]["hosting"]["choice"])
        self.assertTrue("india" in h["regions"] or h["self_hostable"] or "global" in h["regions"])
        self.assertTrue(any("india" in n.lower() for n in o["compliance_notes"]))

    def test_rbi_forces_india_even_without_residency(self):
        o = run(compliance=["rbi_localisation"], requirements__payments=True)
        self.assertTrue(any("rbi" in a.lower() and "india" in a.lower() for a in o["assumptions"]))
        pay = [c for c in o["stack"]["supporting"] if c["layer"] == "payments"][0]["choice"]
        self.assertIn(pay, ("Razorpay", "Cashfree Payments", "PayU"))

    def test_rbi_with_eu_residency_is_critical(self):
        o = run(compliance=["rbi_localisation"], infrastructure__data_residency="eu")
        self.assertIn("RBI_RESIDENCY_CONFLICT", codes(o))

    def test_hipaa_note_mentions_baa(self):
        o = run(compliance=["hipaa"])
        self.assertTrue(any("BAA" in n for n in o["compliance_notes"]))

    def test_availability_vs_solo_beginner_is_critical(self):
        o = run(requirements__availability="99.99", team__size=1, team__experience="beginner")
        self.assertTrue(any(w["code"] == "AVAILABILITY_VS_TEAM" and w["severity"] == "critical" for w in o["warnings"]))

    def test_huge_scale_tiny_budget_warns(self):
        o = run(scale__users_12_months=5_000_000, scale__users_at_launch=100000, budget__monthly_infra_usd=50)
        self.assertIn("SCALE_VS_BUDGET", codes(o))

    def test_short_timeline_many_platforms_warns(self):
        o = run(timeline__mvp_weeks=2, project__platforms=["web", "android", "ios"])
        self.assertIn("TIMELINE_VS_PLATFORMS", codes(o))

    def test_eol_existing_system_warns_and_is_not_recommended(self):
        o = run(infrastructure__existing_systems=["Python 2.7 monolith"])
        self.assertIn("EOL_EXISTING_SYSTEM", codes(o))
        self.assertTrue(any("Python 2.7" in n for n in o["integration_notes"]))

    def test_existing_sql_server_is_reused(self):
        o = run(infrastructure__existing_systems=["On-prem SQL Server 2019"], team__languages=["csharp", "sql"])
        self.assertEqual(o["stack"]["database"]["choice"], "Microsoft SQL Server")

    def test_entra_id_reused_for_enterprise_sso(self):
        o = run(infrastructure__existing_systems=["Microsoft Entra ID (Azure AD)"], requirements__auth="enterprise_sso", team__languages=["csharp"])
        auth = [c for c in o["stack"]["supporting"] if c["layer"] == "auth"][0]
        self.assertEqual(auth["choice"], "Microsoft Entra ID")

    def test_offline_support_selects_sync_capable_database(self):
        o = run(requirements__offline_support=True, project__platforms=["android"], project__type="other")
        k = kbmod.load()
        self.assertIn("offline_sync", k.get("database", o["stack"]["database"]["choice"])["tags"])

    def test_realtime_adds_realtime_component_and_websocket_host(self):
        o = run(requirements__realtime=True)
        self.assertTrue(any(c["layer"] == "realtime" for c in o["stack"]["supporting"]))
        self.assertTrue(kbmod.load().get("hosting", o["stack"]["hosting"]["choice"])["websockets"])

    def test_payments_add_payment_gateway_outside_india(self):
        o = run(requirements__payments=True)
        pay = [c for c in o["stack"]["supporting"] if c["layer"] == "payments"][0]["choice"]
        self.assertIn(pay, ("Stripe", "Adyen"))

    def test_every_component_has_alternatives_and_counterfactuals(self):
        o = run(requirements__payments=True, requirements__file_media_storage=True)
        for layer in ("frontend", "backend", "database", "hosting"):
            c = o["stack"][layer]
            self.assertTrue(c["alternatives"], layer)
            self.assertTrue(c["what_would_change"], layer)
            for a in c["alternatives"]:
                self.assertGreaterEqual(len(a["why_not"]), 25)

    def test_driven_by_paths_are_real_input_fields(self):
        o = run(requirements__payments=True, requirements__realtime=True, compliance=["gdpr"])
        groups = [o["stack"][k] for k in ("frontend", "backend", "database", "hosting")] + o["stack"]["supporting"]
        for g in groups:
            for p in g["driven_by"]:
                self.assertRegex(p, r"^(project|scale|team|budget|timeline|infrastructure|requirements|compliance|priorities|extra)")

    def test_justification_mentions_input_values(self):
        o = run(budget__monthly_infra_usd=321)
        self.assertIn("321", o["stack"]["hosting"]["justification"])

    def test_cost_band_is_ordered_and_non_negative(self):
        c = run()["estimated_monthly_cost_usd"]
        self.assertGreaterEqual(c["min"], 0)
        self.assertGreaterEqual(c["max"], c["min"])
        self.assertTrue(c["assumptions"])

    def test_budget_overrun_is_flagged(self):
        o = run(budget__monthly_infra_usd=5, scale__users_12_months=900000, scale__users_at_launch=1000)
        self.assertIn("BUDGET_EXCEEDED", codes(o))
        self.assertNotEqual(o["status"], "ok")

    def test_status_ok_has_no_warning_severity(self):
        o = run()
        if o["status"] == "ok":
            self.assertFalse([w for w in o["warnings"] if w["severity"] != "info"])

    def test_api_only_has_no_frontend(self):
        o = run(project__platforms=["api_only"], project__type="api_platform")
        self.assertEqual(o["stack"]["frontend"]["choice"], "None")

    def test_seo_critical_prefers_prerendering_frontend(self):
        o = run(requirements__seo_critical=True, project__type="content_site", requirements__auth="none")
        self.assertIn(o["stack"]["frontend"]["choice"], ("Astro", "Eleventy", "Next.js", "Nuxt", "SvelteKit"))

    def test_mobile_platforms_choose_cross_platform_client(self):
        o = run(project__platforms=["web", "android", "ios"], team__languages=["typescript"])
        self.assertEqual(o["stack"]["frontend"]["choice"], "React Native (Expo)")

    def test_extras_change_output(self):
        a = run()
        raw = mod()
        raw["extra"] = {"vendor_lock_in_tolerance": "low", "data_sensitivity": "restricted", "expected_rps": 3000}
        self.assertNotEqual(json.dumps(a, sort_keys=True), json.dumps(recommend(raw), sort_keys=True))

    def test_engine_never_crashes_on_minimal_valid_input(self):
        raw = {"project": {"type": "other", "platforms": ["web"]}, "scale": {"users_at_launch": 0, "users_12_months": 0},
               "team": {"size": 1, "experience": "beginner", "languages": []}, "budget": {"monthly_infra_usd": 0}, "timeline": {"mvp_weeks": 1}}
        self.assertIn(recommend(raw)["status"], ("ok", "ok_with_warnings", "infeasible"))


if __name__ == "__main__":
    unittest.main()
