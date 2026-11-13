"""Regression tests for defects found by adversarial review rounds (see review/round_N/critique.md)."""
import unittest

from tests.helpers import mod, run
from stacksense import kb as kbmod, recommend


def sup(o, layer):
    return [c["choice"] for c in o["stack"]["supporting"] if c["layer"] == layer]


class Round1Regressions(unittest.TestCase):
    def test_dotnet_auth_library_only_with_dotnet_backend(self):
        o = run(team__languages=["python"], requirements__auth="email_password")
        self.assertNotIn("ASP.NET Core Identity", sup(o, "auth"))

    def test_dotnet_auth_library_allowed_for_dotnet_team(self):
        o = run(team__languages=["csharp"], requirements__auth="email_password", budget__monthly_infra_usd=2000)
        self.assertEqual(o["stack"]["backend"]["choice"], "ASP.NET Core")
        self.assertIn(sup(o, "auth")[0], ("ASP.NET Core Identity", "Firebase Authentication", "Amazon Cognito", "Auth0", "Keycloak", "Microsoft Entra ID"))

    def test_bullmq_needs_node_backend(self):
        o = run(team__languages=["java"], scale__users_12_months=3_000_000, budget__monthly_infra_usd=20000, team__size=8, team__has_devops=True)
        self.assertNotIn("BullMQ", sup(o, "queue"))

    def test_dynamic_app_does_not_get_content_generator(self):
        o = run(project__type="saas_b2b", requirements__multi_tenant=True)
        self.assertNotIn(o["stack"]["frontend"]["choice"], ("Astro", "Eleventy"))

    def test_internal_tool_with_sso_not_on_document_database(self):
        o = run(project__type="internal_tool", requirements__auth="enterprise_sso")
        self.assertNotIn(o["stack"]["database"]["choice"], ("Firestore", "Amazon DynamoDB", "MongoDB Atlas"))

    def test_multitenant_saas_prefers_relational(self):
        k = kbmod.load()
        o = run(project__type="saas_b2b", requirements__multi_tenant=True)
        self.assertIn("relational", k.get("database", o["stack"]["database"]["choice"])["tags"])

    def test_end_of_life_mysql_is_not_reused(self):
        o = run(infrastructure__existing_systems=["MySQL 5.7 database"])
        self.assertIn("EOL_EXISTING_SYSTEM", {w["code"] for w in o["warnings"]})
        self.assertNotEqual(o["stack"]["database"]["choice"], "MySQL")

    def test_end_of_life_rules_cover_databases(self):
        for text in ("MySQL 5.6", "MongoDB 3.6", "PostgreSQL 11", "PostgreSQL 9.6"):
            self.assertIsNotNone(kbmod.lifecycle_issue(text), text)

    def test_android_only_app_gets_no_cdn(self):
        o = run(project__platforms=["android"], requirements__file_media_storage=True, scale__users_12_months=20000, team__languages=["kotlin"])
        self.assertEqual(sup(o, "cdn"), [])

    def test_llm_rag_gets_retrieval_and_generation_components(self):
        o = run(requirements__ml_features="llm_rag", project__type="ai_ml_product")
        self.assertGreaterEqual(len(sup(o, "ml")), 2)
        text = " ".join(c["justification"] for c in o["stack"]["supporting"] if c["layer"] == "ml")
        self.assertIn("retrieval", text)
        self.assertIn("model-serving", text)

    def test_on_premise_training_gets_a_trainable_framework(self):
        o = run(requirements__ml_features="training", infrastructure__deployment_model="on_premise", team__languages=["python"], team__size=4, team__has_devops=True)
        self.assertIn(sup(o, "ml")[0], ("PyTorch", "scikit-learn (self-hosted inference)"))

    def test_licence_matching_is_case_insensitive(self):
        raw = mod()
        raw["extra"] = {"existing_licences": ["Oracle Database Enterprise"]}
        o = recommend(raw)
        self.assertIn("LICENCE_NOT_USED", {w["code"] for w in o["warnings"]})

    def test_static_site_with_huge_traffic_is_cheap_and_only_warned(self):
        o = run(project__type="content_site", requirements__auth="none", scale__users_12_months=8_000_000, scale__workload="read_heavy",
                budget__monthly_infra_usd=100, team__size=1, team__languages=["javascript"])
        self.assertEqual(o["architecture_style"], "static")
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 30)
        w = [x for x in o["warnings"] if x["code"] == "SCALE_VS_BUDGET"]
        self.assertTrue(w and w[0]["severity"] == "warning")

    def test_summary_uses_correct_article(self):
        self.assertIn("an intermediate team", run()["summary"])
        self.assertIn("a beginner team", run(team__experience="beginner")["summary"])

    def test_zero_budget_dynamic_app_prefers_free_tier_hosting(self):
        o = run(budget__monthly_infra_usd=0, team__size=1, team__experience="beginner", team__languages=["javascript"], scale__users_12_months=500, scale__users_at_launch=100)
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 40)

    def test_single_node_hosting_warns_when_scale_exceeds_cap(self):
        o = run(infrastructure__deployment_model="on_premise", scale__users_12_months=400000, scale__users_at_launch=1000, team__size=2)
        codes = {w["code"] for w in o["warnings"]}
        self.assertIn("SINGLE_NODE_CAPACITY", codes)

    def test_zero_cost_supporting_text_is_not_dollar_zero_dash_zero(self):
        o = run(requirements__payments=True, infrastructure__data_residency="india")
        text = " ".join(c["justification"] for c in o["stack"]["supporting"])
        self.assertNotIn("$0-0", text)


if __name__ == "__main__":
    unittest.main()


class Round2Regressions(unittest.TestCase):
    def test_peak_concurrency_raises_the_load_tier(self):
        a = run(scale__users_12_months=5000, scale__peak_concurrent_users=50)
        b = run(scale__users_12_months=5000, scale__peak_concurrent_users=90000, team__size=6, team__has_devops=True, team__experience="senior")
        self.assertGreater(len(b["stack"]["supporting"]), len(a["stack"]["supporting"]))

    def test_sqlite_never_runs_on_ephemeral_hosts(self):
        k = kbmod.load()
        for host in ("Google Cloud Run", "AWS Lambda", "AWS ECS on Fargate", "Azure Container Apps"):
            from stacksense import engine
            self.assertFalse(engine.db_fits_host(k.get("database", "SQLite"), k.get("hosting", host)), host)
        self.assertTrue(engine.db_fits_host(k.get("database", "SQLite"), k.get("hosting", "AWS EC2")))

    def test_azure_gets_a_managed_cache(self):
        o = run(infrastructure__cloud_preference="azure", scale__users_12_months=600000, scale__peak_concurrent_users=20000, team__languages=["csharp"],
                budget__monthly_infra_usd=20000, team__size=8, team__has_devops=True, team__experience="senior")
        self.assertEqual(sup(o, "cache"), ["Azure Managed Redis"])

    def test_htmx_not_chosen_for_realtime_social_apps(self):
        o = run(project__type="social", requirements__realtime=True, team__languages=["java"], scale__users_12_months=100000, budget__monthly_infra_usd=3000)
        self.assertNotEqual(o["stack"]["frontend"]["choice"], "HTMX with server-rendered templates")

    def test_zero_budget_stays_in_free_tiers(self):
        o = run(budget__monthly_infra_usd=0, scale__users_12_months=300, scale__users_at_launch=100, team__size=1, team__experience="beginner", team__languages=["python"])
        self.assertLessEqual(o["estimated_monthly_cost_usd"]["max"], 40)
        self.assertEqual(o["estimated_monthly_cost_usd"]["min"], 0)


    def test_internal_tool_gets_no_cdn_unless_users_are_spread(self):
        o = run(project__type="internal_tool", requirements__file_media_storage=True, scale__peak_concurrent_users=300, scale__users_12_months=1500)
        self.assertEqual(sup(o, "cdn"), [])
