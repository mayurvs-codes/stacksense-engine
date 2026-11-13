p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='        s -= 1.2  # relational integrity, ad-hoc queries and reporting are the sensible default'
new='        s -= 1.8  # relational integrity, ad-hoc queries and reporting are the sensible default'
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
