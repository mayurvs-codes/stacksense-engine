import copy
import unittest

from tests.helpers import base, mod, run
from stacksense.validate import validate


def fields(raw):
    n, errs, _ = validate(raw)
    return n, [e["field"] for e in errs]


class ValidateTests(unittest.TestCase):
    def test_valid_base_has_no_errors(self):
        n, f = fields(base())
        self.assertEqual(f, [])
        self.assertIsNotNone(n)

    def test_empty_object_reports_all_required_fields(self):
        _, f = fields({})
        for req in ("project.type", "project.platforms", "scale.users_at_launch", "scale.users_12_months", "team.size",
                    "team.experience", "team.languages", "budget.monthly_infra_usd", "timeline.mvp_weeks"):
            self.assertIn(req, f)

    def test_non_object_is_rejected(self):
        _, errs, _ = validate([])
        self.assertEqual(errs[0]["field"], "$")

    def test_unknown_enum_rejected(self):
        self.assertIn("project.type", fields(mod(project__type="spaceship"))[1])

    def test_negative_users_rejected(self):
        self.assertIn("scale.users_at_launch", fields(mod(scale__users_at_launch=-1))[1])

    def test_bool_is_not_an_int(self):
        self.assertIn("team__size".replace("__", "."), fields(mod(team__size=True))[1])

    def test_float_team_size_rejected(self):
        self.assertIn("team.size", fields(mod(team__size=2.5))[1])

    def test_integral_float_accepted(self):
        self.assertEqual(fields(mod(team__size=3.0))[1], [])

    def test_empty_platforms_rejected(self):
        self.assertIn("project.platforms", fields(mod(project__platforms=[]))[1])

    def test_priority_out_of_range(self):
        self.assertIn("priorities.cost", fields(mod(priorities__cost=9))[1])
        self.assertIn("priorities.cost", fields(mod(priorities__cost=0))[1])

    def test_p95_zero_rejected_but_null_allowed(self):
        self.assertIn("requirements.p95_latency_ms", fields(mod(requirements__p95_latency_ms=0))[1])
        self.assertEqual(fields(mod(requirements__p95_latency_ms=None))[1], [])

    def test_bad_availability(self):
        self.assertIn("requirements.availability", fields(mod(requirements__availability="100"))[1])

    def test_bad_compliance_item(self):
        self.assertIn("compliance", fields(mod(compliance=["sox"]))[1])

    def test_null_section_reported(self):
        self.assertIn("team", fields(mod(team=None))[1])

    def test_all_errors_reported_together(self):
        f = fields(mod(project__type="x", team__size=-1, budget__monthly_infra_usd="abc"))[1]
        self.assertTrue({"project.type", "team.size", "budget.monthly_infra_usd"} <= set(f))

    def test_defaults_are_recorded_as_assumptions(self):
        raw = base()
        raw["infrastructure"] = {}
        _, _, a = validate(raw)
        text = " ".join(a)
        for key in ("cloud_preference", "deployment_model", "data_residency", "existing_systems"):
            self.assertIn(key, text)

    def test_missing_priorities_recorded(self):
        raw = base()
        del raw["priorities"]
        _, _, a = validate(raw)
        self.assertTrue(any("priorities" in x for x in a))

    def test_unknown_top_level_field_is_ignored_not_fatal(self):
        raw = base()
        raw["mystery"] = 1
        n, errs, a = validate(raw)
        self.assertEqual(errs, [])
        self.assertTrue(any("mystery" in x for x in a))

    def test_extra_parameters_validated(self):
        raw = base()
        raw["extra"] = {"geo_distribution": "mars"}
        self.assertIn("extra.geo_distribution", fields(raw)[1])

    def test_extra_unknown_key_ignored(self):
        raw = base()
        raw["extra"] = {"made_up": 1}
        self.assertEqual(fields(raw)[1], [])

    def test_languages_lowercased(self):
        n, _ = fields(mod(team__languages=["Python", " TypeScript "]))
        self.assertEqual(n["team"]["languages"], ["python", "typescript"])

    def test_languages_may_be_empty(self):
        self.assertEqual(fields(mod(team__languages=[]))[1], [])


if __name__ == "__main__":
    unittest.main()
