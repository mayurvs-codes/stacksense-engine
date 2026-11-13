import unittest

from stacksense import kb as kbmod

CORE = ("frontend", "backend", "database", "hosting")
REQUIRED = ("name", "layer", "lifecycle_status", "languages", "regions", "self_hostable", "saas_only", "cloud", "cost_model", "strengths",
            "limits", "ops_burden", "maturity", "provides", "sources", "ratings", "cost", "tags", "runtimes", "websockets", "hosting_type")


class KBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = kbmod.load()
        cls.entries = [e for layer in cls.kb.layers.values() for e in layer]

    def test_core_layers_have_enough_options(self):
        for layer in CORE:
            self.assertGreaterEqual(len(self.kb.layer(layer)), 8, layer)

    def test_every_entry_has_required_fields(self):
        for e in self.entries:
            for f in REQUIRED:
                self.assertIn(f, e, e["name"])

    def test_every_entry_is_active(self):
        for e in self.entries:
            self.assertEqual(e["lifecycle_status"], "active", e["name"])

    def test_every_entry_has_https_sources_with_audit_dates(self):
        for e in self.entries:
            self.assertTrue(e["sources"], e["name"])
            for s in e["sources"]:
                self.assertTrue(s["url"].startswith("https://"), e["name"])
                self.assertRegex(s["accessed"], r"^2026-\d\d-\d\d$", e["name"] + " has an unverified source")

    def test_no_entry_name_is_end_of_life(self):
        for e in self.entries:
            self.assertIsNone(kbmod.lifecycle_issue(e["name"]), e["name"])

    def test_cloud_tag_matches_name_pattern(self):
        for e in self.entries:
            for cloud, rx in kbmod.CLOUD_PATTERNS.items():
                if rx.search(e["name"]):
                    self.assertEqual(e["cloud"], cloud, e["name"])

    def test_ratings_are_in_range(self):
        for e in self.entries:
            for k, v in e["ratings"].items():
                self.assertIn(v, (1, 2, 3, 4, 5), f"{e['name']} {k}")

    def test_unique_names_per_layer(self):
        for layer, ents in self.kb.layers.items():
            names = [e["name"] for e in ents]
            self.assertEqual(len(names), len(set(names)), layer)

    def test_managed_services_declare_regions(self):
        for e in self.entries:
            if e["saas_only"] and e["layer"] in ("hosting", "database", "storage", "cdn"):
                self.assertTrue(e["regions"], e["name"])

    def test_hyperscaler_entries_record_attestations(self):
        for name in ("AWS ECS on Fargate", "Azure App Service", "Google Cloud Run"):
            self.assertIn("iso27001", self.kb.get("hosting", name)["compliance"])

    def test_lifecycle_rules_catch_known_eol_names(self):
        for text in ("AngularJS 1.8", "Python 2.7 service", "SQL Server 2014", "CentOS 7 host", "Windows Server 2012"):
            self.assertIsNotNone(kbmod.lifecycle_issue(text), text)

    def test_lifecycle_rules_do_not_flag_supported_versions(self):
        for text in ("SQL Server 2019", "PostgreSQL 16", "Python 3.12", "Node.js 22", ".NET 8"):
            self.assertIsNone(kbmod.lifecycle_issue(text), text)

    def test_region_notes_refer_to_real_entries(self):
        for name in self.kb.region_notes:
            self.assertTrue(any(e["name"] == name for e in self.entries), name)


if __name__ == "__main__":
    unittest.main()
