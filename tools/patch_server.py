p='stacksense/server.py'
s=open(p,encoding='utf-8').read()
s=s.replace('        if self.path in ("/", "/index.html"):','        if self.path.split("?")[0] in ("/", "/index.html"):',1)
s=s.replace('        if self.path != "/api/recommend":','        if self.path.split("?")[0] != "/api/recommend":',1)
open(p,'w',encoding='utf-8').write(s)
