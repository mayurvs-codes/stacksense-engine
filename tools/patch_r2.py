import re
p='stacksense/engine.py'
s=open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,1)
# tier by peak concurrency
rep('''    if f.rps is not None:
        trps =''','''    tpeak = 0 if f.peak <= 100 else 1 if f.peak <= 1000 else 2 if f.peak <= 10000 else 3 if f.peak <= 100000 else 4
    f.tier = max(f.tier, tpeak)
    if f.rps is not None:
        trps =''')
# sqlite only on persistent machines
rep('''    if e["name"] == "SQLite":
        return host["hosting_type"] in ("vm", "onprem", "paas", "container")''','''    if e["name"] == "SQLite":
        return host["hosting_type"] in ("vm", "onprem")  # containers and serverless have ephemeral disks''')
# container penalty softer
rep('''    if e["self_hostable"] and not e["saas_only"] and "library" not in t and host["hosting_type"] in ("static", "serverless", "paas", "container"):
        s -= 1.5  # a separate stateful service would need its own compute''','''    if e["self_hostable"] and not e["saas_only"] and "library" not in t:
        ht = host["hosting_type"]
        if ht in ("static", "serverless", "paas"):
            s -= 1.5  # a separate service would need its own compute
        elif ht == "container":
            s -= 0.5  # runs as an extra container, but state needs care''')
# HTMX over-selection
rep('''    if f.static_like and "ssr" in t:
        s -= 0.8''','''    if e["name"].startswith("HTMX"):
        if f.tier >= 3:
            s -= 0.8
        if f.rt:
            s -= 0.8
        if f.type in ("social", "gaming", "realtime_collab"):
            s -= 1.0
    if f.static_like and "ssr" in t:
        s -= 0.8''')
open(p,'w',encoding='utf-8').write(s)

g=open('tools/kb_source.py',encoding='utf-8').read()
g=g.replace('sup("cache", "Google Cloud Memorystore"','''sup("cache", "Azure Managed Redis", cloud="azure", regions=ALLR, saas=True, r=(5, 3, 5, 5, 4, 4), ops=1, tags=("cache",), cost=((15, 150), (1, 10)), cap=100_000_000,
    strengths=("Managed Redis-compatible in-memory data store on Azure",), limits=("Azure lock-in", "Always-on capacity cost"),
    src=[("https://learn.microsoft.com/en-us/azure/redis/overview", "What is Azure Managed Redis")])
sup("cache", "Google Cloud Memorystore"''',1)
g=g.replace('"Amazon ElastiCache": (13, 60), "Google Cloud Memorystore": (13, 60)','"Amazon ElastiCache": (13, 60), "Google Cloud Memorystore": (13, 60), "Azure Managed Redis": (13, 60)',1)
open('tools/kb_source.py','w',encoding='utf-8').write(g)
print("patched")
