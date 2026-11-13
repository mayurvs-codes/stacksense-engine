"""Dev helper: runs the engine on every scenario in a JSON list file and prints a one-line stack summary each."""
import json, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from stacksense import recommend
path = sys.argv[1] if len(sys.argv) > 1 else "data/scenarios/public_scenarios.json"
for s in json.load(open(path, encoding="utf-8")):
    o = recommend(s)
    st = o["stack"]
    if st:
        core = " | ".join(f"{k}={st[k]['choice']}" for k in ("frontend", "backend", "database", "hosting"))
        sup = ", ".join(f"{c['layer']}:{c['choice']}" for c in st["supporting"])
    else:
        core, sup = "-", "-"
    print(f"{s.get('scenario_id')}: {o['status']} {o['architecture_style']} cost={o['estimated_monthly_cost_usd']['min']}-{o['estimated_monthly_cost_usd']['max']}\n   {core}\n   sup: {sup}\n   warn: {[w['code']+':'+w['severity'] for w in o['warnings']]}")
