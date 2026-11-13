p='tools/make_screenshots.py'
s=open(p,encoding='utf-8').read()
s=s.replace('return {s["scenario_id"]: {k: v for k, v in s.items() if k != "_class"} for s in getattr(m, f"build{n}")()}','fn = getattr(m, f"build{n}", None) or getattr(m, "build")\n    return {s["scenario_id"]: {k: v for k, v in s.items() if k != "_class"} for s in fn()}',1)
s=s.replace('        for sid, s in pub.items():\n            print(shot(f"{sid}_result", s))\n        shot("form_P2", pub["P2"], view="f", width=1400, height=1500)\n','',1)
open(p,'w',encoding='utf-8').write(s)
