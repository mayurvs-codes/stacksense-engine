import re
for f in ('README.md', 'docs/REPORT_NOTES.md'):
    t = open(f, encoding='utf-8').read()
    t = t.replace('124 curated technologies', '129 curated technologies').replace('124-entry', '129-entry')
    t = t.replace('124 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 63 supporting', '129 entries: 16 frontend, 11 backend, 17 database, 22 hosting, 63 supporting')
    t = t.replace('has 124 entries', 'has 129 entries')
    t = t.replace("(for example Kubernetes services, Neon, PlanetScale, Hetzner, Fly.io)", "(for example Neon, PlanetScale, Hetzner, Fly.io, CockroachDB)")
    open(f, 'w', encoding='utf-8').write(t)

b = open('tools/build_report.py', encoding='utf-8').read()
b = b.replace("no globally distributed SQL, managed Kubernetes services, media pipelines or .NET desktop clients; Neon, PlanetScale, Hetzner and Fly.io are absent", "no media pipelines, and few niche or regional vendors; Neon, PlanetScale, Hetzner, Fly.io and CockroachDB are absent")
b = b.replace("<li>The Docker image was not built on the development machine.</li>", "<li>The Docker image was built and run once on the development machine (UI and API answered); it was not tested on other platforms.</li>")
b = b.replace("130 unit and property tests", "132 unit and property tests")
open('tools/build_report.py', 'w', encoding='utf-8').write(b)

w = open('tools/write_progress.py', encoding='utf-8').read()
w = w.replace('- Not verified: `docker compose up` (Docker not run on this machine).', '- Docker: the image was built and run on this machine (UI returned 200, API returned a recommendation); `docker compose up` itself was not run.')
w = w.replace('125 unit and property tests', '132 unit and property tests').replace('125 pass', '132 pass').replace('- 125 unit', '- 132 unit')
w = w.replace('Rounds 2-9: adversarial review (`review/round_1` ... `review/round_9`)', 'Rounds 2-9 plus final polish: adversarial review (`review/round_1` ... `review/round_9`)')
w = w.replace('124 entries after round 8', '129 entries (added managed Kubernetes on AWS/GCP/Azure, Cloud Spanner and .NET MAUI with opened sources; Kubernetes now needs high load or a big team)')
w = w.replace('no globally distributed SQL, Kubernetes services or media pipeline in the KB', 'no media pipeline in the KB, and some vendors (Neon, PlanetScale, Hetzner, Fly.io, CockroachDB) are absent')
open('tools/write_progress.py', 'w', encoding='utf-8').write(w)
print('docs patched')
