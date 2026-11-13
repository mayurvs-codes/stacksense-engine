p = 'stacksense/engine.py'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


rep("estimated ${cost_of(h, f)[0]:.0f}-{cost_of(h, f)[1]:.0f}/month at {v('scale.users_12_months', f.u12)}.\")",
    "estimated {money_band(*cost_of(h, f))}/month at {v('scale.users_12_months', f.u12)}.\")")
rep('def explain_host(h, f, kb, comp):', '''def money_band(lo, hi):
    return f"${lo:.0f}" if round(lo) == round(hi) else f"${lo:.0f}-{hi:.0f}"


def explain_host(h, f, kb, comp):''')
rep("cf.why(\"timeline.mvp_weeks\", f\"A {v('timeline.mvp_weeks', f.weeks)}-week timeline favours its time-to-market rating of {fe['ratings']['ttm']}/5.\")",
    "cf.why(\"timeline.mvp_weeks\", f\"A {f.weeks}-week MVP timeline ({v('timeline.mvp_weeks', f.weeks)}) favours its time-to-market rating of {fe['ratings']['ttm']}/5.\")")
open(p, 'w', encoding='utf-8').write(s)

h = open('stacksense/static/index.html', encoding='utf-8').read()
old = ' const c=o.estimated_monthly_cost_usd;h+=`<div class="card"><h2>Estimated monthly cost: $${c.min} to $${c.max}</h2><ul>${c.assumptions.map(a=>`<li>${esc(a)}</li>`).join("")}</ul></div>`;'
new = ' const c=o.estimated_monthly_cost_usd;if(o.stack)h+=`<div class="card"><h2>Estimated monthly cost: ${c.min===c.max?"$"+c.min:"$"+c.min+" to $"+c.max}</h2><ul>${c.assumptions.map(a=>`<li>${esc(a)}</li>`).join("")}</ul></div>`;'
assert old in h
open('stacksense/static/index.html', 'w', encoding='utf-8').write(h.replace(old, new, 1))
print("patched")
