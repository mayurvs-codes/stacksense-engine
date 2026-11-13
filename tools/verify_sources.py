"""Opens every source URL in the knowledge base and records which ones resolve (HTTP 200, real HTML page).
Writes tools/verified.json {url: 'YYYY-MM-DD'} for pages that opened, and tools/verify_report.json with details."""
import json, re, ssl, sys, urllib.request, datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
urls = sorted({s["url"] for f in (ROOT / "data/kb").glob("*.json") for e in json.loads(f.read_text(encoding="utf-8")) for s in e["sources"]})
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def fetch(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            body = r.read(200000).decode("utf-8", "ignore")
            t = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
            return u, r.status, (t.group(1).strip()[:90] if t else ""), len(body), r.geturl()
    except Exception as ex:
        return u, 0, f"{type(ex).__name__}: {str(ex)[:80]}", 0, ""
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(fetch, urls))
today = datetime.date.today().isoformat()
ok = {u: today for u, st, t, n, fin in res if st == 200 and n > 500}
manual = ROOT / "tools/verified_manual.json"  # pages opened by hand in a browser (sites that block scripted clients)
if manual.exists():
    ok.update(json.loads(manual.read_text(encoding="utf-8")))
(ROOT / "tools/verified.json").write_text(json.dumps(ok, indent=1), encoding="utf-8")
(ROOT / "tools/verify_report.json").write_text(json.dumps([dict(url=u, status=st, title=t, bytes=n, final=fin) for u, st, t, n, fin in res], indent=1), encoding="utf-8")
print(len(urls), "urls;", len(ok), "opened OK")
for u, st, t, n, fin in res:
    if u not in ok:
        print("FAIL", st, u, t)
