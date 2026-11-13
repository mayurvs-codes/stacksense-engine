p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='        total += 0.5 * ranked[0][0]'
new='        total += 0.5 * (ranked[0][0] - 3.0)  # relative to a neutral component, so merely having more components never raises the total'
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
