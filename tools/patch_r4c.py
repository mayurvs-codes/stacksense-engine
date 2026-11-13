p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
old='''    if be is None:
        return True
    rts = set(host["runtimes"])'''
new='''    if be is None:
        return True
    if host["hosting_type"] == "static":
        return False  # static hosts serve files; a framework backend needs a real runtime
    rts = set(host["runtimes"])'''
assert old in s
open(p,'w',encoding='utf-8').write(s.replace(old,new,1))
t=open('tests/test_regression.py',encoding='utf-8').read()
t+='''
    def test_framework_backends_never_run_on_static_hosts(self):
        k = kbmod.load()
        from stacksense import engine
        for host in ("Azure Static Web Apps", "Netlify", "Cloudflare Pages", "GitHub Pages", "AWS Amplify Hosting"):
            self.assertFalse(engine.host_ok_for_backend(k.get("hosting", host), k.get("backend", "Django")), host)
'''
open('tests/test_regression.py','w',encoding='utf-8').write(t)
