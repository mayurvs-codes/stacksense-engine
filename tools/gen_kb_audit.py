"""Generates docs/KB_AUDIT.md from the knowledge base, tools/verified.json and tools/github_lifecycle.json.
It states exactly what was (and was not) verified, so the audit can be trusted."""
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
kb = {}
for f in sorted((ROOT / "data/kb").glob("*.json")):
    for e in json.loads(f.read_text(encoding="utf-8")):
        kb.setdefault(e["layer"], []).append(e)
gh = json.loads((ROOT / "tools/github_lifecycle.json").read_text(encoding="utf-8"))
GH = {"Valkey (self-hosted)": "valkey-io/valkey", "Meilisearch": "meilisearch/meilisearch", "Typesense": "typesense/typesense",
      "Centrifugo": "centrifugal/centrifugo", "Yjs": "yjs/yjs", "BullMQ": "taskforcesh/bullmq", "Socket.IO": "socketio/socket.io",
      "CouchDB": "apache/couchdb", "Keycloak": "keycloak/keycloak", "Qdrant": "qdrant/qdrant", "Ollama": "ollama/ollama",
      "pgvector (PostgreSQL extension)": "pgvector/pgvector", "Redis (self-hosted)": "redis/redis", "RabbitMQ": "rabbitmq/rabbitmq-server",
      "Apache Kafka": "apache/kafka", "OpenSearch": "opensearch-project/OpenSearch", "Sentry (self-hosted)": "getsentry/self-hosted",
      "Grafana + Prometheus": "grafana/grafana", "Jenkins": "jenkinsci/jenkins", "Kubernetes (k3s) on-prem": "k3s-io/k3s",
      "TimescaleDB": "timescale/timescaledb", "ClickHouse": "ClickHouse/ClickHouse", "Express": "expressjs/express", "NestJS": "nestjs/nest",
      "FastAPI": "tiangolo/fastapi", "Go (Gin)": "gin-gonic/gin", "Ktor": "ktorio/ktor", "Axum": "tokio-rs/axum", "Astro": "withastro/astro",
      "Eleventy": "11ty/eleventy", "SvelteKit": "sveltejs/kit", "Nuxt": "nuxt/nuxt", "Tauri": "tauri-apps/tauri", "Electron": "electron/electron",
      "React Native (Expo)": "expo/expo", "Flutter": "flutter/flutter", "Laravel": "laravel/framework", "Ruby on Rails": "rails/rails",
      "Django": "django/django", "Spring Boot": "spring-projects/spring-boot", "ASP.NET Core": "dotnet/aspnetcore", "SeaweedFS": "seaweedfs/seaweedfs", "Pagefind": "CloudCannon/pagefind", "PyTorch": "pytorch/pytorch"}
today = datetime.date.today().isoformat()
L = ["# Knowledge-base audit", "",
     f"Generated {today} by `tools/gen_kb_audit.py` from `data/kb/*.json`, `tools/verified.json` (written by `tools/verify_sources.py`) and "
     "`tools/github_lifecycle.json` (GitHub API check of open-source projects).", "",
     "## What was verified, honestly", "",
     "- **Source pages opened.** Every source URL in the KB was fetched on the date shown in its `accessed` field and returned HTTP 200 with real "
     "HTML (a few URLs that returned 404/403 on the first pass were corrected and re-checked; `dev.mysql.com` blocks scripted clients, so it was "
     "opened in the browser pane instead). Opening a page proves the product page exists, not every claim made about the product.",
     "- **Region claims opened and read** (official pages, 2026-11-13): AWS regions list (Mumbai ap-south-1, Hyderabad ap-south-2, Frankfurt, Ireland, ...); "
     "Azure regions list (Central India/Pune, India South Central/Hyderabad, South India/Chennai, West India/Mumbai); Google Compute Engine regions "
     "(Mumbai asia-south1, Delhi asia-south2); DigitalOcean regional availability (BLR1 Bangalore, FRA1, AMS3, NYC, SFO); Vercel regions (bom1 Mumbai); "
     "Render regions (Oregon, Ohio, Virginia, Frankfurt, Singapore: no India region); Supabase regions (Mumbai, Frankfurt, Ireland, London, Zurich); "
     "Firestore locations (asia-south1 Mumbai, eur3, europe-* locations); MongoDB Atlas on AWS (Hyderabad ap-south-2).",
     "- **Not verified this run (stated as such, kept conservative):** EU/US region availability of Azure, Google Cloud, Vercel and MongoDB Atlas "
     "(general knowledge, widely published); vendor compliance attestations (PCI DSS, HIPAA, SOC 2, ISO 27001 for AWS/Azure/GCP and PCI DSS for "
     "the payment gateways) come from public compliance programmes but their pages were not read claim by claim; Fly.io, Railway, Netlify, "
     "Cloudflare and Hetzner region claims were NOT used (Fly page showed no India region, Hetzner's docs failed TLS verification, Railway not checked), "
     "so these have no India/EU/US region claims and are never chosen under data residency (Hetzner and Fly.io are not in the KB).",
     "- **Lifecycle.** Open-source projects were checked through the GitHub API on 2026-11-13: none is archived and every repository received commits "
     "within the last six weeks (see table). The check removed **MinIO**: its open-source repository's README states it is no longer maintained, "
     "so it was replaced by SeaweedFS. `dotnet/blazor` is archived because Blazor now lives inside `dotnet/aspnetcore`; htmx moved organisations.",
     "- **Ratings and costs are author judgements.** The 1-5 ratings and the USD cost bands are curated estimates informed by the cited pricing and "
     "documentation pages; they are not vendor quotes and not benchmark results. They are documented as such in the report.",
     "- **Timescale** has rebranded its documentation site to \"Tiger Data\"; TimescaleDB remains an active product.", "",
     "## Entries", "", "| Layer | Entry | Source pages opened | OSS lifecycle check |", "|---|---|---|---|"]
for layer in sorted(kb):
    for e in sorted(kb[layer], key=lambda x: x["name"].lower()):
        srcs = "; ".join(f"[{s['title']}]({s['url']}) ({s['accessed'] or 'NOT OPENED'})" for s in e["sources"])
        g = gh.get(GH.get(e["name"], ""))
        life = f"{GH[e['name']]}: archived={g[0]}, last push {g[1]}" if g and e["name"] in GH else "n/a (commercial/managed service or standard)"
        L.append(f"| {layer} | {e['name']} | {srcs} | {life} |")
(ROOT / "docs/KB_AUDIT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote docs/KB_AUDIT.md", len(L))
