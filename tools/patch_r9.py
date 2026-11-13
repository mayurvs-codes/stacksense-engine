p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
rep('''        cb.why("team.experience", f"A {v('team.experience', f.exp)} team of {v('team.size', f.team)} gets {be['name']}'s''','''        cb.why("team.experience", f"For a {f.exp} team of {f.team} engineers ({v('team.experience', f.exp)}, {v('team.size', f.team)}), {be['name']} offers {'batteries-included conventions' if 'fullstack' in be['tags'] else 'a typed, structured API model'} (operations burden {be['ops_burden']} vs capacity {f.ops_cap}). Placeholder-end.''')
rep('''(operations burden {be['ops_burden']} vs capacity {f.ops_cap}). Placeholder-end. {'batteries-included conventions' if 'fullstack' in be['tags'] else 'typed, structured API model'} (operations burden {be['ops_burden']} vs capacity {f.ops_cap}).")''','''(operations burden {be['ops_burden']} vs capacity {f.ops_cap}).")''') if False else None
open(p,'w',encoding='utf-8').write(s)
