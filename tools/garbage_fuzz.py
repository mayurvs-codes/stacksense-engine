"""Robustness fuzz: mutate valid scenarios with wrong types / extreme values / unicode; the engine must never raise."""
import copy, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gate")); sys.path.insert(0, str(ROOT))
import run_gate
from stacksense import recommend
r = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
JUNK = [None, "", "x", 0, -1, 1e308, float("nan"), 10**30, [], {}, [None], [[]], True, "😀", "Ünïcode", {"a": 1}, "99.9", 3.5, -0.0]
def paths(d, pre=""):
    for k, v in d.items():
        p = pre + k
        yield p
        if isinstance(v, dict):
            yield from paths(v, p + ".")
bad = crashes = 0
base = run_gate.gen_scenarios(60, 5)
for i in range(3000):
    s = copy.deepcopy(r.choice(base))
    for _ in range(r.randint(1, 4)):
        ps = list(paths(s)); p = r.choice(ps).split(".")
        cur = s
        for k in p[:-1]:
            cur = cur[k] if isinstance(cur.get(k), dict) else {}
        if r.random() < 0.15 and p[-1] in cur:
            del cur[p[-1]]
        else:
            cur[p[-1]] = r.choice(JUNK)
    if r.random() < 0.1:
        s["extra"] = r.choice([{"expected_rps": r.choice(JUNK)}, {"integration_needs": r.choice(JUNK)}, {"geo_distribution": r.choice(JUNK)}, "str", []])
    try:
        o = recommend(s)
        json.dumps(o)
        assert o["status"] in ("ok", "ok_with_warnings", "infeasible", "invalid_input")
        if o["status"] == "invalid_input":
            bad += 1
            assert o["validation_errors"]
    except Exception as ex:
        crashes += 1
        if crashes <= 3:
            print("CRASH", type(ex).__name__, ex, json.dumps(s)[:300])
print("runs 3000 | invalid_input", bad, "| crashes", crashes)
