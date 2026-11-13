import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT, base, fuzz
from stacksense import kb as kbmod, recommend
from stacksense.cli import load_and_recommend


def cli(text, name="in.json"):
    with tempfile.TemporaryDirectory() as td:
        inp, out = Path(td) / name, Path(td) / "out.json"
        inp.write_text(text, encoding="utf-8")
        p = subprocess.run([sys.executable, "-m", "stacksense", "run", str(inp), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        return p, (json.loads(out.read_text(encoding="utf-8")) if out.exists() else None)


class CliTests(unittest.TestCase):
    def test_run_writes_output_and_exits_zero(self):
        p, o = cli(json.dumps(base()))
        self.assertEqual(p.returncode, 0)
        self.assertIn(o["status"], ("ok", "ok_with_warnings"))

    def test_run_invalid_json_gives_invalid_input(self):
        p, o = cli("{nope")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(o["status"], "invalid_input")
        self.assertEqual(o["validation_errors"][0]["field"], "$")

    def test_run_top_level_list_is_invalid_input(self):
        p, o = cli("[]")
        self.assertEqual(o["status"], "invalid_input")

    def test_load_and_recommend_accepts_text(self):
        self.assertIn(load_and_recommend(json.dumps(base()))["status"], ("ok", "ok_with_warnings"))

    def test_cli_output_is_byte_stable(self):
        _, a = cli(json.dumps(base()))
        _, b = cli(json.dumps(base()))
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_missing_file_exits_nonzero(self):
        p = subprocess.run([sys.executable, "-m", "stacksense", "run", "does-not-exist.json"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)


class PropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = kbmod.load()
        cls.cases = [(s, recommend(s)) for s in fuzz(60, 99)]

    def test_hard_constraint_cloud_preference_never_violated(self):
        for s, o in self.cases:
            pref = s["infrastructure"]["cloud_preference"]
            if pref in ("aws", "azure", "gcp") and o["stack"]:
                for layer in ("hosting", "database"):
                    e = self.kb.get(layer, o["stack"][layer]["choice"])
                    if e:
                        self.assertIn(e["cloud"], ("neutral", pref), (s["scenario_id"], e["name"]))
                for c in o["stack"]["supporting"]:
                    e = self.kb.get(c["layer"], c["choice"])
                    self.assertIn(e["cloud"], ("neutral", pref), (s["scenario_id"], e["name"]))

    def test_residency_never_violated_for_managed_stores(self):
        for s, o in self.cases:
            res = s["infrastructure"]["data_residency"]
            if res != "none" and o["stack"]:
                for layer in ("hosting", "database"):
                    e = self.kb.get(layer, o["stack"][layer]["choice"])
                    if e:
                        self.assertTrue(e["self_hostable"] or res in e["regions"] or "global" in e["regions"], (s["scenario_id"], e["name"]))

    def test_on_premise_never_gets_saas(self):
        for s, o in self.cases:
            if s["infrastructure"]["deployment_model"] == "on_premise" and o["stack"]:
                for layer in ("hosting", "database"):
                    e = self.kb.get(layer, o["stack"][layer]["choice"])
                    if e:
                        self.assertTrue(e["self_hostable"] and not e["saas_only"], (s["scenario_id"], e["name"]))

    def test_kubernetes_needs_devops_team(self):
        for s, o in self.cases:
            if not o["stack"]:
                continue
            big = s["team"]["size"] >= 4 and s["team"]["has_devops"]
            names = [o["stack"][k]["choice"] for k in ("hosting", "database")] + [c["choice"] for c in o["stack"]["supporting"]]
            if not big:
                self.assertFalse([n for n in names if "ubernetes" in n or "k3s" in n], s["scenario_id"])

    def test_status_is_consistent_with_warnings(self):
        for s, o in self.cases:
            sev = [w["severity"] for w in o["warnings"]]
            if o["status"] == "ok":
                self.assertFalse([x for x in sev if x != "info"], s["scenario_id"])
            if o["status"] == "ok_with_warnings":
                self.assertTrue(o["warnings"], s["scenario_id"])
            if o["status"] == "infeasible":
                self.assertIn("critical", sev, s["scenario_id"])

    def test_every_valid_input_yields_a_stack_or_clear_infeasibility(self):
        for s, o in self.cases:
            self.assertIn(o["status"], ("ok", "ok_with_warnings", "infeasible"), s["scenario_id"])
            if o["stack"] is None:
                self.assertEqual(o["status"], "infeasible")

    def test_reordering_list_fields_keeps_stack(self):
        for s, o in self.cases[:20]:
            t = json.loads(json.dumps(s))
            t["team"]["languages"] = list(reversed(t["team"]["languages"]))
            t["project"]["platforms"] = list(reversed(t["project"]["platforms"]))
            t["scenario_id"], t["project"]["name"] = "zz", "renamed"
            self.assertEqual(json.dumps(o["stack"], sort_keys=True), json.dumps(recommend(t)["stack"], sort_keys=True), s["scenario_id"])

    def test_small_budget_change_is_local(self):
        for s, o in self.cases[:20]:
            t = json.loads(json.dumps(s))
            t["budget"]["monthly_infra_usd"] = s["budget"]["monthly_infra_usd"] * 1.05 + 1
            o2 = recommend(t)
            if o["stack"] and o2["stack"]:
                diff = sum(o["stack"][k]["choice"] != o2["stack"][k]["choice"] for k in ("frontend", "backend", "database", "hosting"))
                self.assertLessEqual(diff, 2, s["scenario_id"])


if __name__ == "__main__":
    unittest.main()
