p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='''    if nonrel and (f.mt or f.fts or f.type in ("internal_tool", "saas_b2b", "healthtech", "data_analytics")):
        s -= 0.6'''
new='''    if nonrel and (f.mt or f.fts or f.type in ("internal_tool", "saas_b2b", "healthtech", "data_analytics")):
        s -= 0.6
    if nonrel and (f.pay or f.type in ("fintech", "ecommerce", "marketplace")):
        s -= 1.0  # money movement needs ACID transactions'''
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
