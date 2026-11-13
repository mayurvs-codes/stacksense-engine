"""Generates data/kb/*.json (the knowledge base) from compact tables.

Run:  python tools/kb_source.py            (writes data/kb/*.json; deterministic)
Ratings are curated author judgements on a 1-5 scale (5 = best) and are documented as such in docs/REPORT_NOTES.md.
Costs are order-of-magnitude monthly USD estimates: fixed + per_1k_users * (users_12_months / 1000).
`verified_on` per source is filled in from tools/verified.json, which is written only by the page-opening audit.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIED = {}
vf = Path(__file__).resolve().parent / "verified.json"
if vf.exists():
    VERIFIED = json.loads(vf.read_text(encoding="utf-8"))

ALLR = ["india", "eu", "us", "other"]  # hyperscaler regions covering the residency enum values
E = []


def add(layer, name, *, langs=(), regions=(), self_host=False, saas=False, cloud="neutral", r=(3, 3, 3, 3, 3, 3), ops=2,
        cost=((0, 0), (0, 0)), tags=(), fts=False, plat=(), runtimes=(), ws=True, htype="", cap=1_000_000,
        maturity="mature", strengths=(), limits=(), comp=(), src=(), provides=()):
    ttm, cst, scl, prf, mnt, sec = r
    if layer in ("frontend", "backend"):
        self_host = True  # frameworks are software you deploy yourself
    verified = [{"url": u, "title": t, "accessed": VERIFIED.get(u, "")} for u, t in src]
    E.append({
        "name": name, "layer": layer, "lifecycle_status": "active", "languages": list(langs), "regions": list(regions),
        "self_hostable": self_host, "saas_only": saas, "cloud": cloud,
        "cost_model": "estimate: fixed %s + per-1k-users %s USD/month" % (list(cost[0]), [round(x * 0.1, 3) for x in cost[1]]),
        "cost": {"fixed": list(cost[0]), "per_1k_users": [round(x * 0.1, 3) for x in cost[1]]},
        "strengths": list(strengths), "limits": list(limits), "ops_burden": ops, "maturity": maturity,
        "provides": list(provides), "fts": fts, "ratings": {"ttm": ttm, "cost": cst, "scale": scl, "perf": prf, "maint": mnt, "sec": sec},
        "tags": list(tags), "platforms": list(plat), "runtimes": list(runtimes), "websockets": ws, "hosting_type": htype,
        "scale_cap_users": cap, "compliance": list(comp), "sources": verified,
    })


# ------------------------------------------------------------------ FRONTEND
F = "frontend"
add(F, "Astro", langs=("javascript", "typescript"), plat=("web",), r=(5, 5, 4, 5, 4, 4), ops=1, tags=("static", "ssg", "seo"), cap=5_000_000,
    strengths=("Pre-renders pages to static HTML with minimal client JavaScript", "Markdown/MDX content collections built in"),
    limits=("Highly interactive apps need islands/hydration", "Not a full application framework"),
    src=[("https://docs.astro.build/en/concepts/why-astro/", "Why Astro")])
add(F, "Eleventy", langs=("javascript",), plat=("web",), r=(5, 5, 3, 5, 4, 4), ops=1, tags=("static", "ssg", "seo", "simple"), cap=5_000_000,
    strengths=("Very small learning curve: templates plus Markdown to static HTML", "No client framework required"),
    limits=("Little built-in interactivity", "Smaller ecosystem than React-based generators"),
    src=[("https://www.11ty.dev/docs/", "Eleventy docs")])
add(F, "Next.js", langs=("javascript", "typescript"), plat=("web",), r=(5, 3, 5, 4, 4, 4), ops=2, tags=("ssr", "seo", "react", "fullstack"), runtimes=("node",), cap=20_000_000,
    strengths=("Server rendering, static generation and API routes in one React framework", "Very large ecosystem and hiring pool"),
    limits=("Needs a Node runtime for SSR", "Framework complexity and frequent major changes"),
    src=[("https://nextjs.org/docs", "Next.js docs")])
add(F, "React (Vite)", langs=("javascript", "typescript"), plat=("web",), r=(4, 4, 4, 3, 4, 4), ops=1, tags=("spa", "react"), cap=20_000_000,
    strengths=("Fast dev tooling and the largest component ecosystem", "Deploys as static files behind any CDN"),
    limits=("Client-side rendering is weak for SEO without extra work", "You assemble routing/state/data libraries yourself"),
    src=[("https://react.dev/", "React"), ("https://vite.dev/guide/", "Vite guide")])
add(F, "Nuxt", langs=("javascript", "typescript"), plat=("web",), r=(4, 3, 4, 4, 4, 4), ops=2, tags=("ssr", "seo", "vue", "fullstack"), runtimes=("node",), cap=10_000_000,
    strengths=("Vue meta-framework with SSR, static generation and file-based routing", "Gentle learning curve for Vue teams"),
    limits=("Smaller hiring pool than React", "SSR needs a Node runtime"),
    src=[("https://nuxt.com/docs", "Nuxt docs")])
add(F, "SvelteKit", langs=("javascript", "typescript"), plat=("web",), r=(4, 4, 4, 5, 4, 4), ops=2, tags=("ssr", "seo", "svelte", "fullstack"), runtimes=("node",), cap=10_000_000,
    strengths=("Compiles to small, fast bundles", "Simple reactive model that beginners pick up quickly"),
    limits=("Smaller ecosystem and talent pool", "Fewer enterprise-grade component libraries"),
    src=[("https://svelte.dev/docs/kit", "SvelteKit docs")])
add(F, "Angular", langs=("typescript",), plat=("web",), r=(3, 3, 5, 4, 5, 4), ops=2, tags=("spa", "enterprise"), cap=20_000_000,
    strengths=("Opinionated, batteries-included structure that scales across large teams", "Strong typing and long-term support cadence"),
    limits=("Steeper learning curve", "Heavier for small sites"),
    src=[("https://angular.dev/overview", "Angular overview")])
add(F, "Blazor", langs=("csharp",), plat=("web",), r=(4, 4, 4, 3, 5, 4), ops=2, tags=("spa", "dotnet", "enterprise"), runtimes=("dotnet",), cap=5_000_000,
    strengths=("Full-stack C# for the UI, reusing .NET skills and libraries", "Tight integration with ASP.NET Core and Entra ID"),
    limits=("Smaller ecosystem than JavaScript frameworks", "Interactive server mode needs persistent connections"),
    src=[("https://learn.microsoft.com/en-us/aspnet/core/blazor/", "Blazor overview")])
add(F, "HTMX with server-rendered templates", langs=(), plat=("web",), r=(5, 5, 3, 4, 5, 4), ops=1, tags=("ssr", "seo", "simple", "internal"), cap=2_000_000,
    strengths=("Server-side templates in the backend's own language with small client footprint", "Great for internal tools and CRUD apps"),
    limits=("Rich client-side interactions need extra JavaScript", "Offline and mobile use cases are out of scope"),
    src=[("https://htmx.org/docs/", "htmx docs")])
add(F, "Flutter", langs=("dart",), plat=("android", "ios", "web", "desktop"), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("mobile_cross", "offline_ok"), cap=20_000_000,
    strengths=("One codebase for Android, iOS, web and desktop", "Consistent UI and good performance"),
    limits=("Requires Dart", "Web output is weaker for SEO"),
    src=[("https://docs.flutter.dev/", "Flutter docs")])
add(F, "React Native (Expo)", langs=("javascript", "typescript"), plat=("android", "ios", "web"), r=(5, 4, 4, 3, 4, 4), ops=1, tags=("mobile_cross", "offline_ok", "react"), cap=20_000_000,
    strengths=("Shares JavaScript/TypeScript skills across Android, iOS and web", "Managed builds and over-the-air updates via Expo"),
    limits=("Native modules can force ejecting from the managed workflow", "Lower raw performance than native"),
    src=[("https://docs.expo.dev/", "Expo docs")])
add(F, "Kotlin (Jetpack Compose)", langs=("kotlin", "java"), plat=("android",), r=(3, 4, 4, 5, 4, 5), ops=1, tags=("mobile_native", "offline_ok"), cap=20_000_000,
    strengths=("Native Android performance and full platform API access", "Strong offline storage options"),
    limits=("Android only", "Separate codebase needed for iOS and web"),
    src=[("https://developer.android.com/compose", "Jetpack Compose")])
add(F, "Swift (SwiftUI)", langs=("swift",), plat=("ios",), r=(3, 4, 4, 5, 4, 5), ops=1, tags=("mobile_native", "offline_ok"), cap=20_000_000,
    strengths=("Native iOS quality and platform integration",), limits=("iOS only", "Requires Apple tooling and Swift skills"),
    src=[("https://developer.apple.com/swiftui/", "SwiftUI")])
add(F, "Electron", langs=("javascript", "typescript"), plat=("desktop", "web"), r=(4, 4, 3, 3, 4, 3), ops=1, tags=("desktop",), cap=5_000_000,
    strengths=("Desktop apps from web skills", "Mature packaging and auto-update tooling"),
    limits=("Large memory and install footprint", "Security hardening is your responsibility"),
    src=[("https://www.electronjs.org/docs/latest/", "Electron docs")])
add(F, "Tauri", langs=("rust", "javascript", "typescript"), plat=("desktop",), r=(3, 4, 3, 4, 4, 4), ops=1, tags=("desktop",), cap=5_000_000,
    strengths=("Small, fast desktop bundles using the system webview",), limits=("Rust backend code required for native features", "Younger ecosystem"),
    src=[("https://tauri.app/start/", "Tauri docs")])

# ------------------------------------------------------------------- BACKEND
B = "backend"
add(B, "FastAPI", langs=("python",), runtimes=("python",), r=(5, 4, 4, 4, 4, 4), ops=2, tags=("api", "ml_friendly"), cap=2_000_000,
    strengths=("Fast to build typed REST APIs with automatic OpenAPI docs", "Natural fit when ML models are in Python"),
    limits=("Async ecosystem needs care", "Fewer batteries (admin, ORM) than Django"),
    src=[("https://fastapi.tiangolo.com/", "FastAPI")])
add(B, "Django", langs=("python",), runtimes=("python",), r=(5, 4, 4, 3, 5, 4), ops=2, tags=("fullstack", "admin"), cap=2_000_000,
    strengths=("Batteries-included: ORM, auth, admin, migrations", "Long track record and stable release cadence"),
    limits=("Monolithic conventions", "Real-time features need Channels/ASGI add-ons"),
    src=[("https://docs.djangoproject.com/en/stable/", "Django docs")])
add(B, "NestJS", langs=("typescript", "javascript"), runtimes=("node",), r=(4, 4, 4, 4, 5, 4), ops=2, tags=("api", "enterprise", "realtime_ok"), cap=3_000_000,
    strengths=("Structured TypeScript architecture with modules and dependency injection", "First-class WebSocket gateways"),
    limits=("Opinionated and verbose for tiny services", "Node single-thread limits for CPU-bound work"),
    src=[("https://docs.nestjs.com/", "NestJS docs")])
add(B, "Express", langs=("javascript", "typescript"), runtimes=("node",), r=(5, 5, 3, 3, 3, 3), ops=1, tags=("api", "simple", "realtime_ok"), cap=500_000,
    strengths=("Minimal and ubiquitous Node web framework", "Largest tutorial and middleware ecosystem"),
    limits=("No enforced structure; security middleware is your job", "Maintenance burden grows with the codebase"),
    src=[("https://expressjs.com/", "Express")])
add(B, "Spring Boot", langs=("java", "kotlin"), runtimes=("java",), r=(3, 3, 5, 4, 5, 5), ops=3, tags=("enterprise", "fintech_ok", "api"), cap=50_000_000,
    strengths=("Mature, security-oriented enterprise framework with huge library support", "Strong transactions and observability integrations"),
    limits=("Heavier memory/startup footprint", "Steeper learning curve and more boilerplate"),
    src=[("https://spring.io/projects/spring-boot", "Spring Boot")])
add(B, "ASP.NET Core", langs=("csharp",), runtimes=("dotnet",), r=(4, 4, 5, 5, 5, 5), ops=2, tags=("enterprise", "api", "dotnet"), cap=50_000_000,
    strengths=("High-performance, cross-platform framework with first-class Entra ID and SQL Server support", "Strong tooling and typed end-to-end"),
    limits=("Smaller open-source ecosystem than Java/JS", "Licensing/hosting choices bias toward Microsoft stack"),
    src=[("https://learn.microsoft.com/en-us/aspnet/core/introduction-to-aspnet-core", "ASP.NET Core")])
add(B, "Laravel", langs=("php",), runtimes=("php",), r=(5, 4, 3, 3, 4, 4), ops=2, tags=("fullstack", "admin"), cap=1_000_000,
    strengths=("Rapid development with auth, queues and ORM built in", "Excellent documentation"),
    limits=("PHP runtime scaling needs care", "Fewer fintech/ML libraries"),
    src=[("https://laravel.com/docs", "Laravel docs")])
add(B, "Go (Gin)", langs=("go",), runtimes=("go",), r=(3, 5, 5, 5, 4, 4), ops=2, tags=("api", "realtime_ok", "perf"), cap=20_000_000,
    strengths=("Very low latency and memory use; single static binary", "Excellent concurrency for websocket/realtime servers"),
    limits=("More boilerplate than dynamic frameworks", "Smaller batteries-included ecosystem"),
    src=[("https://gin-gonic.com/", "Gin docs")])
add(B, "Ruby on Rails", langs=("ruby",), runtimes=("ruby",), r=(5, 4, 3, 3, 4, 4), ops=2, tags=("fullstack", "admin"), cap=1_000_000,
    strengths=("Convention-over-configuration speed for CRUD products",), limits=("Throughput limits at very high scale", "Shrinking talent pool"),
    src=[("https://guides.rubyonrails.org/", "Rails Guides")])
add(B, "Ktor", langs=("kotlin",), runtimes=("java",), r=(4, 4, 4, 4, 4, 4), ops=2, tags=("api", "kotlin"), cap=5_000_000,
    strengths=("Lightweight Kotlin server framework with coroutines",), limits=("Smaller ecosystem than Spring", "Fewer ready-made enterprise modules"),
    src=[("https://ktor.io/docs/welcome.html", "Ktor docs")])
add(B, "Axum", langs=("rust",), runtimes=("rust",), r=(2, 5, 5, 5, 4, 5), ops=2, tags=("api", "perf"), cap=20_000_000,
    strengths=("Memory-safe, very high performance Rust web framework",), limits=("Steep learning curve and slower iteration", "Small hiring pool"),
    src=[("https://docs.rs/axum/latest/axum/", "Axum docs")])

# ------------------------------------------------------------------ DATABASE
D = "database"
add(D, "SQLite", langs=("sql",), r=(5, 5, 2, 4, 4, 3), ops=1, tags=("embedded", "small"), fts=True, cap=20_000, self_host=True,
    strengths=("Zero-ops single-file database with FTS5 search", "Excellent for prototypes, small internal tools and local-first apps"),
    limits=("Single writer; not for concurrent multi-server writes", "Backups/replication are your job"),
    src=[("https://www.sqlite.org/about.html", "About SQLite")])
add(D, "PostgreSQL", langs=("sql",), r=(4, 5, 4, 4, 5, 4), ops=3, self_host=True, cost=((10, 80), (2, 16)), fts=True, tags=("relational", "fts", "json", "multitenant"), cap=50_000_000,
    strengths=("Robust relational engine with JSONB, full-text search, extensions (PostGIS, pgvector)", "No licence cost; every cloud offers it managed"),
    limits=("Self-managed means you own patching, backups and failover", "Vertical scaling first; sharding is complex"),
    src=[("https://www.postgresql.org/about/", "About PostgreSQL")])
add(D, "MySQL", langs=("sql",), r=(4, 5, 4, 4, 4, 4), ops=3, self_host=True, cost=((10, 80), (2, 16)), fts=True, tags=("relational",), cap=20_000_000,
    strengths=("Widely known relational database with a huge hosting ecosystem",), limits=("Fewer advanced features than PostgreSQL", "Licence/edition nuances"),
    src=[("https://dev.mysql.com/doc/", "MySQL Community Edition")])
add(D, "Microsoft SQL Server", langs=("sql", "csharp"), r=(4, 2, 5, 4, 5, 5), ops=3, self_host=True, cost=((150, 900), (4, 32)), fts=True, tags=("relational", "dotnet", "enterprise"), cap=50_000_000,
    strengths=("Deep .NET and Microsoft ecosystem integration", "Mature tooling, reporting and security features"),
    limits=("Licensing cost unless existing licences are reused", "Linux/container operations less common"),
    src=[("https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2022", "SQL Server docs")])
add(D, "MongoDB Atlas", langs=("javascript", "typescript", "python", "java"), regions=("india", "eu", "us"), saas=True, r=(5, 3, 4, 4, 3, 4), ops=1, tags=("document",), cap=20_000_000,
    cost=((0, 60), (5, 40)),
    strengths=("Flexible document model with managed clusters on AWS, Azure and GCP", "Atlas Search built in"),
    limits=("Joins/transactions are weaker than relational", "Costs rise quickly with dedicated clusters"),
    src=[("https://www.mongodb.com/docs/atlas/reference/amazon-aws/", "Atlas on AWS regions")])
add(D, "Amazon Aurora PostgreSQL", langs=("sql",), cloud="aws", regions=ALLR, saas=True, r=(4, 2, 5, 5, 4, 5), ops=2, fts=True, tags=("relational", "managed", "multitenant"), cap=100_000_000,
    cost=((60, 250), (10, 60)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed PostgreSQL-compatible engine with Multi-AZ storage and fast failover", "Available in Mumbai and Hyderabad regions"),
    limits=("Higher cost than plain RDS at small scale", "AWS lock-in"),
    src=[("https://aws.amazon.com/rds/aurora/", "Amazon Aurora")])
add(D, "Amazon RDS for PostgreSQL", langs=("sql",), cloud="aws", regions=ALLR, saas=True, r=(5, 3, 4, 4, 4, 5), ops=2, fts=True, tags=("relational", "managed", "multitenant"), cap=20_000_000,
    cost=((15, 120), (4, 30)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed PostgreSQL with automated backups and Multi-AZ option", "Low operational burden for small teams"),
    limits=("Instance sizing is manual", "AWS lock-in"),
    src=[("https://aws.amazon.com/rds/postgresql/", "Amazon RDS for PostgreSQL")])
add(D, "Azure SQL Database", langs=("sql", "csharp"), cloud="azure", regions=ALLR, saas=True, r=(5, 3, 4, 4, 5, 5), ops=1, fts=True, tags=("relational", "managed", "dotnet", "enterprise"), cap=50_000_000,
    cost=((5, 150), (3, 30)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed SQL Server engine with Entra ID integration", "Easy migration path from on-premises SQL Server"),
    limits=("Azure lock-in", "Cost grows with DTU/vCore tier"),
    src=[("https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview", "Azure SQL Database")])
add(D, "Azure Database for PostgreSQL", langs=("sql",), cloud="azure", regions=ALLR, saas=True, r=(5, 3, 4, 4, 4, 5), ops=2, fts=True, tags=("relational", "managed"), cap=20_000_000,
    cost=((15, 130), (4, 30)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed PostgreSQL flexible server in Azure regions including India",), limits=("Azure lock-in",),
    src=[("https://learn.microsoft.com/en-us/azure/postgresql/", "Azure Database for PostgreSQL")])
add(D, "Google Cloud SQL for PostgreSQL", langs=("sql",), cloud="gcp", regions=ALLR, saas=True, r=(5, 3, 4, 4, 4, 5), ops=2, fts=True, tags=("relational", "managed", "multitenant"), cap=20_000_000,
    cost=((10, 120), (4, 30)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed PostgreSQL in Mumbai (asia-south1) and Delhi (asia-south2)", "Simple pairing with Cloud Run"),
    limits=("GCP lock-in", "Instance sizing is manual"),
    src=[("https://cloud.google.com/sql/docs/postgres", "Cloud SQL for PostgreSQL")])
add(D, "Firestore", langs=("javascript", "typescript", "python", "kotlin", "java", "dart"), cloud="gcp", regions=ALLR, saas=True, r=(5, 4, 5, 4, 3, 4), ops=1,
    tags=("document", "offline_sync", "realtime", "mobile"), cap=50_000_000, cost=((0, 25), (2, 25)), comp=("soc2", "iso27001", "gdpr"),
    strengths=("Offline persistence and automatic sync in the mobile SDKs", "Mumbai (asia-south1) and EU multi-region locations available"),
    limits=("Limited querying (no joins/aggregations at scale)", "Per-operation pricing can surprise write-heavy workloads"),
    src=[("https://firebase.google.com/docs/firestore/locations", "Firestore locations")])
add(D, "Amazon DynamoDB", langs=("javascript", "typescript", "python", "java", "go", "csharp"), cloud="aws", regions=ALLR, saas=True, r=(3, 3, 5, 5, 3, 5), ops=1,
    tags=("kv", "serverless"), cap=100_000_000, cost=((0, 40), (3, 40)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Single-digit-millisecond key-value access at any scale", "Serverless capacity modes"),
    limits=("Access patterns must be designed up front", "No ad-hoc relational queries"),
    src=[("https://aws.amazon.com/dynamodb/", "Amazon DynamoDB")])
add(D, "Supabase Postgres", langs=("sql", "javascript", "typescript"), regions=("india", "eu", "us"), saas=True, r=(5, 4, 3, 4, 4, 4), ops=1, fts=True,
    tags=("relational", "managed", "multitenant", "realtime"), cap=1_000_000, cost=((0, 60), (3, 25)),
    strengths=("Managed PostgreSQL with Mumbai and Frankfurt/Ireland regions", "Row-level security supports multi-tenancy"),
    limits=("Smaller operator than hyperscalers; plan limits apply", "Scaling beyond mid-size needs higher tiers"),
    src=[("https://supabase.com/docs/guides/platform/regions", "Supabase regions")])
add(D, "CouchDB", langs=("javascript",), self_host=True, cost=((10, 70), (2, 12)), r=(3, 4, 3, 3, 3, 3), ops=3, tags=("document", "offline_sync"), cap=500_000,
    strengths=("Built-in multi-master replication, a natural fit for offline-first sync with PouchDB",), limits=("You operate and secure it yourself", "Fewer managed offerings"),
    src=[("https://docs.couchdb.org/en/stable/intro/overview.html", "CouchDB overview")])
add(D, "TimescaleDB", langs=("sql",), self_host=True, cost=((15, 100), (3, 16)), r=(3, 4, 4, 4, 4, 4), ops=3, fts=True, tags=("timeseries", "relational", "iot"), cap=20_000_000,
    strengths=("PostgreSQL extension tuned for time-series ingestion and queries",), limits=("Operational burden of self-hosting", "Requires PostgreSQL skills"),
    src=[("https://docs.timescale.com/", "Timescale docs")])
add(D, "ClickHouse", langs=("sql",), self_host=True, cost=((30, 300), (4, 20)), r=(3, 4, 5, 5, 3, 4), ops=4, tags=("analytics", "columnar"), cap=100_000_000,
    strengths=("Column-store built for fast analytical queries over huge datasets",), limits=("Not a transactional store", "Needs experienced operators"),
    src=[("https://clickhouse.com/docs/en/intro", "ClickHouse intro")])

# ------------------------------------------------------------------- HOSTING
H = "hosting"
add(H, "GitHub Pages", regions=("global",), saas=True, htype="static", runtimes=("static",), ws=False, r=(5, 5, 3, 4, 4, 3), ops=1, tags=("static", "free"), cap=2_000_000,
    cost=((0, 0), (0, 0)), strengths=("Free static hosting directly from a repository",), limits=("Static files only; usage limits apply", "No server-side code or private data"),
    src=[("https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages", "About GitHub Pages")])
add(H, "Cloudflare Pages", regions=("global",), saas=True, htype="static", runtimes=("static",), ws=False, r=(5, 5, 5, 5, 4, 4), ops=1, tags=("static", "free", "cdn"), cap=20_000_000,
    cost=((0, 20), (0, 1)), strengths=("Free static hosting on a global edge network", "Git-based deploys with preview builds"),
    limits=("Static-first; dynamic code runs as edge functions", "Edge network is global, not region-pinned"),
    src=[("https://developers.cloudflare.com/pages/", "Cloudflare Pages")])
add(H, "Netlify", regions=("global",), saas=True, htype="static", runtimes=("static", "node"), ws=False, r=(5, 4, 4, 4, 4, 4), ops=1, tags=("static", "free", "serverless_fn"), cap=5_000_000,
    cost=((0, 20), (0, 3)), strengths=("Free tier with git deploys, forms and serverless functions", "Very low operational burden"),
    limits=("Function execution limits", "Costs rise with bandwidth beyond the free tier"),
    src=[("https://docs.netlify.com/", "Netlify docs")])
add(H, "Vercel", regions=("india", "eu", "us"), saas=True, htype="serverless", runtimes=("node", "static"), ws=False, r=(5, 3, 4, 4, 4, 4), ops=1, tags=("serverless", "ssr", "nextjs"), cap=10_000_000,
    cost=((0, 40), (1, 8)), strengths=("Best-in-class Next.js hosting with preview deployments", "Functions can run in Mumbai (bom1)"),
    limits=("No persistent websocket servers", "Pricing grows with usage; vendor lock-in for Next.js features"),
    src=[("https://vercel.com/docs/regions", "Vercel regions")])
add(H, "Render", regions=("eu", "us"), saas=True, htype="paas", runtimes=("node", "python", "ruby", "go", "docker", "static"), ws=True, r=(5, 4, 3, 3, 4, 3), ops=1, tags=("paas",), cap=200_000,
    cost=((7, 60), (2, 12)), strengths=("Simple git-to-deploy PaaS with managed Postgres and Redis", "Regions: Oregon, Ohio, Virginia, Frankfurt, Singapore"),
    limits=("No India region", "Fewer compliance attestations than hyperscalers"),
    src=[("https://render.com/docs/regions", "Render regions")])
add(H, "DigitalOcean Droplets", regions=("india", "eu", "us"), saas=True, htype="vm", runtimes=("any",), ws=True, r=(3, 5, 3, 3, 3, 3), ops=3, tags=("vm", "cheap"), cap=100_000,
    cost=((12, 120), (1, 8)), strengths=("Low-cost Linux VMs with a Bangalore (BLR1) region", "Predictable flat pricing"),
    limits=("You manage the OS, patching and scaling", "Smaller compliance footprint than hyperscalers"),
    src=[("https://docs.digitalocean.com/platform/regional-availability/", "DigitalOcean regional availability")])
add(H, "AWS ECS on Fargate", cloud="aws", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(3, 3, 5, 4, 4, 5), ops=3, tags=("container", "managed"), cap=50_000_000,
    cost=((40, 400), (8, 60)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Serverless containers without managing servers", "Runs in Mumbai and Hyderabad; deep IAM/VPC controls"),
    limits=("AWS complexity: VPC, IAM, load balancers", "Higher floor cost than simple PaaS"),
    src=[("https://aws.amazon.com/fargate/", "AWS Fargate")])
add(H, "AWS EC2", cloud="aws", regions=ALLR, saas=True, htype="vm", runtimes=("any",), ws=True, r=(2, 3, 5, 4, 3, 4), ops=4, tags=("vm",), cap=50_000_000,
    cost=((15, 300), (3, 25)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Full control over virtual machines", "Wide instance choice in Mumbai and Hyderabad"),
    limits=("You operate OS, scaling and patching", "Easy to over-provision"),
    src=[("https://aws.amazon.com/ec2/", "Amazon EC2")])
add(H, "AWS Lambda", cloud="aws", regions=ALLR, saas=True, htype="serverless", runtimes=("node", "python", "java", "dotnet", "go", "ruby"), ws=False, r=(4, 5, 5, 3, 3, 4), ops=2, tags=("serverless",), cap=100_000_000,
    cost=((0, 40), (1, 10)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Pay-per-invocation scaling to zero", "No servers to patch"),
    limits=("Cold starts affect tail latency", "No long-lived websocket servers without extra services"),
    src=[("https://aws.amazon.com/lambda/", "AWS Lambda")])
add(H, "AWS Amplify Hosting", cloud="aws", regions=ALLR, saas=True, htype="static", runtimes=("static", "node"), ws=False, r=(5, 4, 4, 4, 4, 4), ops=1, tags=("static", "ssr"), cap=5_000_000,
    cost=((0, 30), (1, 6)), comp=("soc2", "iso27001", "gdpr"),
    strengths=("Git-based hosting for static and SSR web apps inside AWS",), limits=("Fewer knobs than Vercel for Next.js", "AWS lock-in"),
    src=[("https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html", "AWS Amplify Hosting")])
add(H, "Azure App Service", cloud="azure", regions=ALLR, saas=True, htype="paas", runtimes=("node", "python", "java", "dotnet", "php", "docker"), ws=True, r=(5, 3, 4, 4, 5, 5), ops=1, tags=("paas", "dotnet", "enterprise"), cap=5_000_000,
    cost=((13, 250), (3, 25)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Fully managed web hosting with Entra ID integration and slots", "Central India (Pune) and other Indian regions"),
    limits=("Azure lock-in", "Scaling tiers jump in price"),
    src=[("https://learn.microsoft.com/en-us/azure/app-service/overview", "Azure App Service")])
add(H, "Azure Static Web Apps", cloud="azure", regions=ALLR, saas=True, htype="static", runtimes=("static", "node", "python", "dotnet"), ws=False, r=(5, 5, 4, 4, 4, 4), ops=1, tags=("static", "free"), cap=5_000_000,
    cost=((0, 9), (0, 2)), comp=("soc2", "iso27001", "gdpr"),
    strengths=("Free tier static hosting with managed API functions",), limits=("Limited to static front-ends and functions",),
    src=[("https://learn.microsoft.com/en-us/azure/static-web-apps/overview", "Azure Static Web Apps")])
add(H, "Azure Container Apps", cloud="azure", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(4, 3, 5, 4, 4, 5), ops=2, tags=("container", "managed"), cap=50_000_000,
    cost=((20, 300), (5, 40)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Serverless containers with scale-to-zero and Dapr/KEDA support",), limits=("Younger than App Service", "Azure lock-in"),
    src=[("https://learn.microsoft.com/en-us/azure/container-apps/overview", "Azure Container Apps")])
add(H, "Azure Virtual Machines", cloud="azure", regions=ALLR, saas=True, htype="vm", runtimes=("any",), ws=True, r=(2, 3, 5, 4, 3, 4), ops=4, tags=("vm",), cap=50_000_000,
    cost=((15, 300), (3, 25)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Full control, Windows and Linux images, hybrid connectivity",), limits=("You operate OS patching and scaling",),
    src=[("https://learn.microsoft.com/en-us/azure/virtual-machines/overview", "Azure Virtual Machines")])
add(H, "Google Cloud Run", cloud="gcp", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(5, 4, 5, 4, 4, 5), ops=2, tags=("container", "managed"), cap=50_000_000,
    cost=((0, 120), (2, 25)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Serverless containers that scale to zero, with websocket support", "Runs in Mumbai (asia-south1) and Delhi (asia-south2)"),
    limits=("Cold starts for scale-to-zero services", "GCP lock-in for surrounding services"),
    src=[("https://cloud.google.com/run/docs/overview/what-is-cloud-run", "What is Cloud Run")])
add(H, "Google Compute Engine", cloud="gcp", regions=ALLR, saas=True, htype="vm", runtimes=("any",), ws=True, r=(2, 3, 5, 4, 3, 4), ops=4, tags=("vm",), cap=50_000_000,
    cost=((15, 300), (3, 25)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Flexible VMs with per-second billing",), limits=("You operate OS patching and scaling",),
    src=[("https://docs.cloud.google.com/compute/docs/regions-zones", "Compute Engine regions and zones")])
add(H, "Docker Compose on a Linux VM", self_host=True, htype="onprem", runtimes=("any", "docker"), ws=True, r=(4, 5, 2, 3, 4, 3), ops=3, tags=("onprem", "simple"), cap=200_000,
    cost=((0, 60), (0, 3)), strengths=("Simple, portable deployment you can run anywhere including an air gap",), limits=("Single host unless you add orchestration", "You own patching, backups and failover"),
    src=[("https://docs.docker.com/compose/", "Docker Compose")])
add(H, "Linux server (systemd + Nginx)", self_host=True, htype="onprem", runtimes=("any",), ws=True, r=(4, 5, 2, 3, 3, 3), ops=3, tags=("onprem", "simple"), cap=100_000,
    cost=((0, 40), (0, 2)), strengths=("Minimal moving parts: a process manager plus a reverse proxy",), limits=("Manual scaling and failover", "You own OS hardening"),
    src=[("https://nginx.org/en/docs/", "nginx documentation")])
add(H, "Kubernetes (k3s) on-prem", self_host=True, htype="onprem", runtimes=("any", "docker"), ws=True, r=(2, 3, 5, 4, 3, 4), ops=5, tags=("onprem", "kubernetes"), cap=50_000_000,
    cost=((0, 200), (0, 5)), strengths=("Lightweight certified Kubernetes for self-managed clusters",), limits=("Requires real platform-engineering capacity",),
    src=[("https://docs.k3s.io/", "K3s documentation")])

# ---------------------------------------------------------------- SUPPORTING
S = dict
def sup(layer, name, **kw):
    add(layer, name, **kw)

# cache
sup("cache", "Redis (self-hosted)", langs=(), self_host=True, r=(4, 5, 4, 5, 4, 3), ops=2, tags=("cache",), cost=((0, 20), (0, 1)), cap=50_000_000,
    strengths=("In-memory cache, pub/sub and queues in one tool",), limits=("Persistence/failover need configuration", "Memory-bound cost"),
    src=[("https://redis.io/docs/latest/", "Redis docs")])
sup("cache", "Valkey (self-hosted)", self_host=True, r=(4, 5, 4, 5, 4, 3), ops=2, tags=("cache",), cost=((0, 20), (0, 1)), cap=50_000_000,
    strengths=("Open-source Redis-compatible fork under the Linux Foundation",), limits=("Newer ecosystem than Redis",),
    src=[("https://valkey.io/", "Valkey")])
sup("cache", "Amazon ElastiCache", cloud="aws", regions=ALLR, saas=True, r=(5, 3, 5, 5, 4, 4), ops=1, tags=("cache",), cost=((13, 150), (1, 10)), cap=100_000_000,
    strengths=("Managed Redis/Valkey/Memcached in AWS regions",), limits=("AWS lock-in", "Always-on node cost"),
    src=[("https://aws.amazon.com/elasticache/", "Amazon ElastiCache")])
sup("cache", "Google Cloud Memorystore", cloud="gcp", regions=ALLR, saas=True, r=(5, 3, 5, 5, 4, 4), ops=1, tags=("cache",), cost=((15, 150), (1, 10)), cap=100_000_000,
    strengths=("Managed Redis/Valkey on Google Cloud",), limits=("GCP lock-in", "Always-on instance cost"),
    src=[("https://cloud.google.com/memorystore/docs", "Memorystore docs")])
# queue
sup("queue", "RabbitMQ", self_host=True, r=(4, 5, 4, 4, 4, 4), ops=3, tags=("queue",), cost=((0, 30), (0, 2)), cap=50_000_000,
    strengths=("Mature message broker with flexible routing",), limits=("Clustering/HA operations are your job",),
    src=[("https://www.rabbitmq.com/docs", "RabbitMQ docs")])
sup("queue", "BullMQ", langs=("javascript", "typescript"), self_host=True, r=(5, 5, 3, 4, 4, 3), ops=1, tags=("queue",), cost=((0, 0), (0, 0)), cap=2_000_000,
    strengths=("Redis-backed job queue for Node with retries and scheduling",), limits=("Requires Redis", "Node ecosystem only"),
    src=[("https://docs.bullmq.io/", "BullMQ docs")])
sup("queue", "Apache Kafka", self_host=True, r=(2, 3, 5, 5, 3, 4), ops=5, tags=("queue", "streaming"), cost=((50, 600), (0, 10)), cap=500_000_000,
    strengths=("Durable high-throughput event streaming",), limits=("Heavy operations burden", "Overkill for small systems"),
    src=[("https://kafka.apache.org/documentation/", "Kafka documentation")])
sup("queue", "Amazon SQS", cloud="aws", regions=ALLR, saas=True, r=(5, 5, 5, 4, 4, 4), ops=1, tags=("queue",), cost=((0, 10), (0, 1)), cap=500_000_000,
    strengths=("Zero-ops managed queue with generous free tier",), limits=("AWS lock-in", "At-least-once semantics"),
    src=[("https://aws.amazon.com/sqs/", "Amazon SQS")])
sup("queue", "Google Cloud Pub/Sub", cloud="gcp", regions=ALLR, saas=True, r=(5, 4, 5, 4, 4, 4), ops=1, tags=("queue",), cost=((0, 20), (0, 2)), cap=500_000_000,
    strengths=("Managed global messaging with push and pull delivery",), limits=("GCP lock-in",),
    src=[("https://cloud.google.com/pubsub/docs/overview", "Pub/Sub overview")])
sup("queue", "Azure Service Bus", cloud="azure", regions=ALLR, saas=True, r=(5, 3, 4, 4, 4, 5), ops=1, tags=("queue", "enterprise"), cost=((0, 40), (0, 2)), cap=100_000_000,
    strengths=("Enterprise messaging with topics, sessions and dead-lettering",), limits=("Azure lock-in",),
    src=[("https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview", "Azure Service Bus")])
# search
sup("search", "Meilisearch", self_host=True, r=(5, 5, 3, 5, 4, 3), ops=2, tags=("search",), cost=((0, 30), (0, 2)), cap=5_000_000,
    strengths=("Typo-tolerant instant search that is simple to run",), limits=("Single-node scaling limits", "Less analytics than OpenSearch"),
    src=[("https://www.meilisearch.com/docs", "Meilisearch docs")])
sup("search", "Typesense", self_host=True, r=(5, 5, 3, 5, 4, 3), ops=2, tags=("search",), cost=((0, 30), (0, 2)), cap=5_000_000,
    strengths=("Fast in-memory typo-tolerant search with a clean API",), limits=("RAM-bound indexes",),
    src=[("https://typesense.org/docs/", "Typesense docs")])
sup("search", "OpenSearch", self_host=True, r=(3, 4, 5, 4, 3, 4), ops=4, tags=("search", "analytics"), cost=((30, 400), (1, 10)), cap=500_000_000,
    strengths=("Scalable full-text and analytics search under Apache 2.0",), limits=("Cluster operations are heavy",),
    src=[("https://opensearch.org/docs/latest/", "OpenSearch docs")])
sup("search", "Algolia", saas=True, regions=("us", "eu"), r=(5, 2, 5, 5, 5, 4), ops=1, tags=("search",), cost=((0, 100), (5, 60)), cap=50_000_000,
    strengths=("Hosted search with excellent relevance tooling",), limits=("Usage-based pricing grows fast", "Data leaves your infrastructure"),
    src=[("https://www.algolia.com/doc/", "Algolia docs")])
# auth
sup("auth", "Keycloak", self_host=True, r=(3, 5, 4, 4, 4, 5), ops=3, tags=("auth", "sso", "enterprise"), cost=((0, 30), (0, 1)), cap=50_000_000,
    strengths=("Self-hostable identity and SSO (OIDC/SAML) with social login",), limits=("You operate and upgrade it", "Phone OTP needs custom SPI/SMS provider"),
    src=[("https://www.keycloak.org/documentation", "Keycloak docs")])
sup("auth", "Firebase Authentication", cloud="neutral", saas=True, regions=("global",), r=(5, 4, 5, 4, 4, 4), ops=1, tags=("auth", "phone_otp", "social", "email"), cost=((0, 10), (0, 6)), cap=100_000_000,
    strengths=("Phone OTP, email/password and social sign-in with SDKs for web and mobile",), limits=("Google-operated; SMS cost per verification", "Data location is not region-pinnable on the basic tier"),
    src=[("https://firebase.google.com/docs/auth", "Firebase Authentication")])
sup("auth", "Amazon Cognito", cloud="aws", regions=ALLR, saas=True, r=(4, 4, 5, 4, 3, 5), ops=2, tags=("auth", "phone_otp", "social", "email", "sso"), cost=((0, 20), (0, 8)), cap=100_000_000,
    strengths=("Managed user pools with SMS OTP, social and SAML sign-in",), limits=("Customisation limits", "AWS lock-in"),
    src=[("https://aws.amazon.com/cognito/", "Amazon Cognito")])
sup("auth", "Microsoft Entra ID", saas=True, regions=("global",), r=(5, 4, 5, 4, 5, 5), ops=1, tags=("auth", "sso", "enterprise"), cost=((0, 20), (0, 2)), cap=100_000_000,
    strengths=("Enterprise single sign-on for Microsoft 365 organisations",), limits=("Designed for workforce identity, not consumer sign-up",),
    src=[("https://learn.microsoft.com/en-us/entra/fundamentals/whatis", "What is Microsoft Entra ID")])
sup("auth", "Auth0", saas=True, regions=("us", "eu"), r=(5, 2, 5, 4, 4, 5), ops=1, tags=("auth", "social", "email", "sso", "phone_otp"), cost=((0, 240), (3, 40)), cap=100_000_000,
    strengths=("Full-featured hosted identity with social, SSO and passwordless",), limits=("Per-MAU pricing grows quickly", "Not hosted in India"),
    src=[("https://auth0.com/docs", "Auth0 docs")])
sup("auth", "ASP.NET Core Identity", langs=("csharp",), self_host=True, r=(5, 5, 3, 4, 4, 4), ops=1, tags=("auth", "email", "dotnet"), cost=((0, 0), (0, 0)), cap=5_000_000,
    strengths=("Built-in membership system for ASP.NET Core apps",), limits=("Email/password focus; SSO needs extra providers",),
    src=[("https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity", "ASP.NET Core Identity")])
# storage
sup("storage", "Amazon S3", cloud="aws", regions=ALLR, saas=True, r=(5, 4, 5, 4, 5, 5), ops=1, tags=("storage",), cost=((0, 10), (0.5, 3)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Durable object storage with regions in Mumbai and Hyderabad",), limits=("Egress costs", "AWS lock-in"),
    src=[("https://aws.amazon.com/s3/", "Amazon S3")])
sup("storage", "Azure Blob Storage", cloud="azure", regions=ALLR, saas=True, r=(5, 4, 5, 4, 5, 5), ops=1, tags=("storage",), cost=((0, 10), (0.5, 3)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Object storage with Indian regions and Entra ID access control",), limits=("Azure lock-in",),
    src=[("https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction", "Azure Blob Storage")])
sup("storage", "Google Cloud Storage", cloud="gcp", regions=ALLR, saas=True, r=(5, 4, 5, 4, 5, 5), ops=1, tags=("storage",), cost=((0, 10), (0.5, 3)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Object storage with Mumbai (asia-south1) and Delhi buckets",), limits=("GCP lock-in",),
    src=[("https://cloud.google.com/storage/docs/introduction", "Cloud Storage introduction")])
sup("storage", "SeaweedFS", self_host=True, r=(3, 5, 4, 4, 4, 4), ops=3, tags=("storage",), cost=((0, 30), (0, 2)), cap=100_000_000,
    strengths=("Open-source distributed object/file store with an S3-compatible API that runs on-premises or in an air gap",), limits=("You operate durability, upgrades and backups", "Smaller community than the hyperscaler services"),
    src=[("https://github.com/seaweedfs/seaweedfs", "SeaweedFS repository")])
sup("storage", "Cloudflare R2", saas=True, regions=("eu", "us"), r=(5, 5, 5, 4, 4, 4), ops=1, tags=("storage",), cost=((0, 10), (0.3, 2)), cap=500_000_000,
    strengths=("S3-compatible storage with zero egress fees and EU jurisdiction option",), limits=("No India jurisdiction",),
    src=[("https://developers.cloudflare.com/r2/", "Cloudflare R2")])
# cdn
sup("cdn", "Cloudflare CDN", saas=True, regions=("global",), r=(5, 5, 5, 5, 5, 4), ops=1, tags=("cdn",), cost=((0, 20), (0, 1)), cap=1_000_000_000,
    strengths=("Global CDN with a free plan, DDoS protection and caching rules",), limits=("Edge network is global, not region-pinned",),
    src=[("https://developers.cloudflare.com/cache/", "Cloudflare Cache docs")])
sup("cdn", "Amazon CloudFront", cloud="aws", regions=("global",), saas=True, r=(5, 4, 5, 5, 4, 4), ops=1, tags=("cdn",), cost=((0, 30), (0, 4)), cap=1_000_000_000,
    strengths=("Global CDN tightly integrated with S3 and AWS WAF",), limits=("AWS lock-in", "Egress-based pricing"),
    src=[("https://aws.amazon.com/cloudfront/", "Amazon CloudFront")])
sup("cdn", "Azure Front Door", cloud="azure", regions=("global",), saas=True, r=(5, 3, 5, 5, 4, 4), ops=1, tags=("cdn",), cost=((35, 120), (0, 4)), cap=1_000_000_000,
    strengths=("Global CDN and load balancer with WAF for Azure workloads",), limits=("Azure lock-in", "Base fee"),
    src=[("https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview", "Azure Front Door")])
sup("cdn", "Google Cloud CDN", cloud="gcp", regions=("global",), saas=True, r=(5, 4, 5, 5, 4, 4), ops=1, tags=("cdn",), cost=((0, 30), (0, 4)), cap=1_000_000_000,
    strengths=("Edge caching for Google Cloud load-balanced backends",), limits=("GCP lock-in",),
    src=[("https://cloud.google.com/cdn/docs/overview", "Cloud CDN overview")])
# realtime
sup("realtime", "Socket.IO", langs=("javascript", "typescript"), self_host=True, r=(5, 5, 3, 4, 4, 3), ops=2, tags=("realtime",), cost=((0, 0), (0, 2)), cap=500_000,
    strengths=("Battle-tested websocket library with rooms and reconnection",), limits=("Scaling out needs a Redis adapter and sticky sessions",),
    src=[("https://socket.io/docs/v4/", "Socket.IO docs")])
sup("realtime", "Centrifugo", self_host=True, r=(4, 5, 5, 5, 4, 4), ops=2, tags=("realtime",), cost=((0, 40), (0, 2)), cap=50_000_000,
    strengths=("Standalone real-time messaging server for any backend language",), limits=("An extra service to run",),
    src=[("https://centrifugal.dev/docs/getting-started/introduction", "Centrifugo introduction")])
sup("realtime", "Yjs", langs=("javascript", "typescript"), self_host=True, r=(4, 5, 5, 5, 4, 3), ops=2, tags=("realtime", "crdt", "collab"), cost=((0, 40), (0, 2)), cap=10_000_000,
    strengths=("CRDT library for conflict-free collaborative editing with live presence",), limits=("Needs a websocket provider/persistence layer",),
    src=[("https://docs.yjs.dev/", "Yjs docs")])
sup("realtime", "Ably", saas=True, regions=("us", "eu"), r=(5, 2, 5, 5, 4, 4), ops=1, tags=("realtime",), cost=((0, 120), (5, 40)), cap=100_000_000,
    strengths=("Managed pub/sub and presence with global edge",), limits=("Cost scales with messages and connections", "Not hosted in India"),
    src=[("https://ably.com/docs", "Ably docs")])
sup("realtime", "Pusher Channels", saas=True, regions=("us", "eu"), r=(5, 3, 4, 4, 4, 4), ops=1, tags=("realtime",), cost=((0, 100), (3, 30)), cap=10_000_000,
    strengths=("Simple hosted websockets with presence channels",), limits=("Connection-based pricing", "Not hosted in India"),
    src=[("https://pusher.com/docs/channels/", "Pusher Channels docs")])
# payments
sup("payments", "Razorpay", saas=True, regions=("india",), r=(5, 4, 5, 5, 5, 5), ops=1, tags=("payments", "upi"), cost=((0, 0), (0, 0)), cap=500_000_000, comp=("pci_dss",),
    strengths=("UPI, cards, netbanking and EMI for Indian merchants", "India-based processing and settlement"),
    limits=("India-focused; limited international coverage", "Transaction-percentage fees"),
    src=[("https://razorpay.com/docs/", "Razorpay docs")])
sup("payments", "Cashfree Payments", saas=True, regions=("india",), r=(5, 4, 4, 4, 4, 5), ops=1, tags=("payments", "upi", "payouts"), cost=((0, 0), (0, 0)), cap=500_000_000, comp=("pci_dss",),
    strengths=("UPI collections and payouts for Indian businesses",), limits=("India-focused", "Transaction-percentage fees"),
    src=[("https://docs.cashfree.com/", "Cashfree docs")])
sup("payments", "PayU", saas=True, regions=("india",), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("payments", "upi"), cost=((0, 0), (0, 0)), cap=500_000_000, comp=("pci_dss",),
    strengths=("Established Indian payment gateway with wide method coverage",), limits=("Integration experience varies", "Transaction fees"),
    src=[("https://docs.payu.in/", "PayU docs")])
sup("payments", "Stripe", saas=True, regions=("us", "eu"), r=(5, 4, 5, 5, 5, 5), ops=1, tags=("payments", "subscriptions", "global"), cost=((0, 0), (0, 0)), cap=500_000_000, comp=("pci_dss",),
    strengths=("Best-in-class developer experience; subscriptions and per-seat billing", "PCI DSS Level 1 service provider"),
    limits=("Transaction-percentage fees", "Not the default choice for India-only UPI flows"),
    src=[("https://docs.stripe.com/", "Stripe docs")])
sup("payments", "Adyen", saas=True, regions=("us", "eu"), r=(4, 3, 5, 5, 4, 5), ops=1, tags=("payments", "enterprise", "global"), cost=((0, 0), (0, 0)), cap=500_000_000, comp=("pci_dss",),
    strengths=("Single platform for global enterprise payments",), limits=("Onboarding aimed at larger merchants",),
    src=[("https://docs.adyen.com/", "Adyen docs")])
# ml
sup("ml", "scikit-learn (self-hosted inference)", langs=("python",), self_host=True, r=(4, 5, 3, 3, 4, 4), ops=2, tags=("ml", "inference"), cost=((0, 20), (0, 2)), cap=5_000_000,
    strengths=("Classical ML (scoring, classification) trained and served in-process",), limits=("Not for deep learning or large models",),
    src=[("https://scikit-learn.org/stable/", "scikit-learn")])
sup("ml", "ONNX Runtime", self_host=True, r=(4, 5, 4, 5, 4, 4), ops=2, tags=("ml", "inference"), cost=((0, 20), (0, 2)), cap=50_000_000,
    strengths=("Portable, fast inference for models exported from many frameworks",), limits=("Model export step required",),
    src=[("https://onnxruntime.ai/docs/", "ONNX Runtime docs")])
sup("ml", "Amazon SageMaker", cloud="aws", regions=ALLR, saas=True, r=(4, 2, 5, 4, 4, 5), ops=2, tags=("ml", "inference", "training"), cost=((30, 600), (2, 30)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001"),
    strengths=("Managed training and real-time inference endpoints",), limits=("Cost and complexity", "AWS lock-in"),
    src=[("https://aws.amazon.com/sagemaker/", "Amazon SageMaker")])
sup("ml", "Google Vertex AI", cloud="gcp", regions=ALLR, saas=True, r=(4, 2, 5, 4, 4, 5), ops=2, tags=("ml", "inference", "training"), cost=((30, 600), (2, 30)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001"),
    strengths=("Managed training, endpoints and model registry",), limits=("Cost and complexity", "GCP lock-in"),
    src=[("https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform", "Vertex AI introduction")])
sup("ml", "Azure Machine Learning", cloud="azure", regions=ALLR, saas=True, r=(4, 2, 5, 4, 4, 5), ops=2, tags=("ml", "inference", "training"), cost=((30, 600), (2, 30)), cap=500_000_000, comp=("pci_dss", "hipaa", "soc2", "iso27001"),
    strengths=("Managed ML lifecycle integrated with Azure DevOps and Entra ID",), limits=("Cost and complexity", "Azure lock-in"),
    src=[("https://learn.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-machine-learning", "What is Azure Machine Learning")])
sup("ml", "pgvector (PostgreSQL extension)", self_host=True, r=(5, 5, 3, 4, 4, 4), ops=2, tags=("ml", "vector", "llm_rag"), cost=((0, 10), (0, 1)), cap=5_000_000,
    strengths=("Vector similarity search inside PostgreSQL for retrieval-augmented generation",), limits=("Large vector workloads outgrow it",),
    src=[("https://github.com/pgvector/pgvector", "pgvector")])
sup("ml", "Qdrant", self_host=True, r=(4, 4, 5, 5, 4, 4), ops=2, tags=("ml", "vector", "llm_rag"), cost=((0, 50), (0, 3)), cap=100_000_000,
    strengths=("Dedicated open-source vector database",), limits=("An extra datastore to operate",),
    src=[("https://qdrant.tech/documentation/", "Qdrant docs")])
sup("ml", "Ollama", self_host=True, r=(4, 5, 2, 3, 4, 4), ops=3, tags=("ml", "llm", "llm_rag", "inference"), cost=((0, 200), (0, 5)), cap=500_000,
    strengths=("Runs open-weight language models locally or on-premises",), limits=("Needs GPU/CPU capacity; smaller models than hosted APIs",),
    src=[("https://github.com/ollama/ollama", "Ollama")])
# ci_cd
sup("ci_cd", "GitHub Actions", saas=True, regions=("global",), r=(5, 5, 4, 4, 4, 4), ops=1, tags=("ci_cd",), cost=((0, 10), (0, 0)), cap=1_000_000_000,
    strengths=("CI/CD built into the repository with a large action marketplace",), limits=("Hosted runners are SaaS; self-hosted runners needed for air gaps",),
    src=[("https://docs.github.com/en/actions", "GitHub Actions docs")])
sup("ci_cd", "GitLab CI/CD (self-managed)", self_host=True, r=(4, 4, 4, 4, 4, 4), ops=3, tags=("ci_cd",), cost=((0, 40), (0, 0)), cap=1_000_000_000,
    strengths=("Complete DevOps platform you can run on-premises",), limits=("Operating GitLab is a real workload",),
    src=[("https://docs.gitlab.com/ee/ci/", "GitLab CI/CD docs")])
sup("ci_cd", "Jenkins", self_host=True, r=(3, 5, 4, 3, 3, 3), ops=4, tags=("ci_cd",), cost=((0, 30), (0, 0)), cap=1_000_000_000,
    strengths=("Self-hosted automation server with a vast plugin ecosystem",), limits=("Plugin maintenance and security upkeep",),
    src=[("https://www.jenkins.io/doc/", "Jenkins docs")])
sup("ci_cd", "Azure DevOps Pipelines", cloud="azure", saas=True, regions=("global",), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("ci_cd", "enterprise"), cost=((0, 30), (0, 0)), cap=1_000_000_000,
    strengths=("CI/CD integrated with Azure Boards, Repos and Entra ID",), limits=("Best inside the Microsoft ecosystem",),
    src=[("https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines", "Azure Pipelines")])
sup("ci_cd", "Google Cloud Build", cloud="gcp", saas=True, regions=("global",), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("ci_cd",), cost=((0, 20), (0, 0)), cap=1_000_000_000,
    strengths=("Serverless CI/CD running in your Google Cloud project",), limits=("GCP lock-in",),
    src=[("https://cloud.google.com/build/docs/overview", "Cloud Build overview")])
sup("ci_cd", "AWS CodePipeline", cloud="aws", saas=True, regions=("global",), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("ci_cd",), cost=((0, 10), (0, 0)), cap=1_000_000_000,
    strengths=("Managed release pipelines inside AWS",), limits=("AWS lock-in", "Less ergonomic than repo-native CI"),
    src=[("https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html", "AWS CodePipeline")])
# observability
sup("observability", "Grafana + Prometheus", self_host=True, r=(3, 5, 4, 4, 4, 4), ops=3, tags=("observability",), cost=((0, 40), (0, 2)), cap=1_000_000_000,
    strengths=("Open-source metrics and dashboards that run anywhere",), limits=("You operate storage and alerting",),
    src=[("https://prometheus.io/docs/introduction/overview/", "Prometheus overview"), ("https://grafana.com/docs/grafana/latest/", "Grafana docs")])
sup("observability", "Sentry (self-hosted)", self_host=True, r=(4, 5, 3, 4, 4, 4), ops=3, tags=("observability", "errors"), cost=((0, 40), (0, 2)), cap=50_000_000,
    strengths=("Error and performance monitoring you can host yourself",), limits=("Resource-hungry to self-host",),
    src=[("https://develop.sentry.dev/self-hosted/", "Sentry self-hosted")])
sup("observability", "Sentry", saas=True, regions=("us", "eu"), r=(5, 4, 5, 4, 5, 4), ops=1, tags=("observability", "errors"), cost=((0, 80), (0, 5)), cap=500_000_000,
    strengths=("Hosted error and performance monitoring with generous free tier",), limits=("Data stored in US/EU only",),
    src=[("https://docs.sentry.io/", "Sentry docs")])
sup("observability", "Datadog", saas=True, regions=("us", "eu"), r=(5, 2, 5, 5, 5, 4), ops=1, tags=("observability", "enterprise"), cost=((20, 500), (2, 30)), cap=1_000_000_000,
    strengths=("Full-stack monitoring, APM and logs in one product",), limits=("Expensive at scale", "Data stored in US/EU/other Datadog sites"),
    src=[("https://docs.datadoghq.com/", "Datadog docs")])
sup("observability", "Amazon CloudWatch", cloud="aws", regions=ALLR, saas=True, r=(5, 4, 5, 4, 4, 5), ops=1, tags=("observability",), cost=((0, 40), (0, 4)), cap=1_000_000_000,
    strengths=("Native metrics, logs and alarms for AWS",), limits=("AWS only", "Log ingestion costs"),
    src=[("https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html", "What is CloudWatch")])
sup("observability", "Azure Monitor", cloud="azure", regions=ALLR, saas=True, r=(5, 4, 5, 4, 4, 5), ops=1, tags=("observability",), cost=((0, 40), (0, 4)), cap=1_000_000_000,
    strengths=("Native monitoring, Application Insights and alerts for Azure",), limits=("Azure only",),
    src=[("https://learn.microsoft.com/en-us/azure/azure-monitor/overview", "Azure Monitor overview")])
sup("observability", "Google Cloud Operations Suite", cloud="gcp", regions=ALLR, saas=True, r=(5, 4, 5, 4, 4, 5), ops=1, tags=("observability",), cost=((0, 40), (0, 4)), cap=1_000_000_000,
    strengths=("Native logging, monitoring and tracing for Google Cloud",), limits=("GCP only",),
    src=[("https://cloud.google.com/products/operations", "Google Cloud Observability")])


LIB = {"Socket.IO", "BullMQ", "Yjs", "scikit-learn (self-hosted inference)", "ONNX Runtime", "ASP.NET Core Identity", "pgvector (PostgreSQL extension)"}


# fixed monthly cost calibration for small deployments (min, max) USD; per-user growth comes from per_1k_users
FIXED_OVR = {"Google Cloud Run": (0, 15), "AWS Lambda": (0, 10), "AWS ECS on Fargate": (30, 120), "Azure App Service": (13, 60),
             "Azure Container Apps": (0, 40), "Vercel": (0, 20), "Netlify": (0, 19), "Render": (7, 25), "DigitalOcean Droplets": (6, 40),
             "AWS EC2": (8, 60), "Google Compute Engine": (8, 60), "Azure Virtual Machines": (8, 60), "AWS Amplify Hosting": (0, 15),
             "Amazon ElastiCache": (13, 60), "Google Cloud Memorystore": (13, 60), "Google Cloud SQL for PostgreSQL": (10, 70),
             "Amazon RDS for PostgreSQL": (15, 80), "Azure SQL Database": (5, 60), "Azure Database for PostgreSQL": (15, 70),
             "Amazon CloudWatch": (0, 15), "Azure Monitor": (0, 15), "Google Cloud Operations Suite": (0, 15), "Cloudflare Pages": (0, 0),
             "Cloudflare CDN": (0, 20), "Azure Static Web Apps": (0, 9), "Amazon CloudFront": (0, 20), "Google Cloud CDN": (0, 20)}
PER1K_OVR = {"Cloudflare Pages": (0, 0.02), "Netlify": (0, 0.3), "GitHub Pages": (0, 0), "Azure Static Web Apps": (0, 0.1), "AWS Amplify Hosting": (0, 0.3)}


def main():
    for e in E:
        if e["name"] in FIXED_OVR:
            e["cost"]["fixed"] = list(FIXED_OVR[e["name"]])
        if e["name"] in PER1K_OVR:
            e["cost"]["per_1k_users"] = list(PER1K_OVR[e["name"]])
        e["cost_model"] = "estimate: fixed %s + per-1k-users %s USD/month" % (e["cost"]["fixed"], e["cost"]["per_1k_users"])
    for e in E:
        if e["name"] in LIB and "library" not in e["tags"]:
            e["tags"].append("library")
    out = ROOT / "data" / "kb"
    out.mkdir(parents=True, exist_ok=True)
    groups = {"frontend": [], "backend": [], "database": [], "hosting": [], "supporting": []}
    for e in E:
        groups[e["layer"] if e["layer"] in groups else "supporting"].append(e)
    for k, v in groups.items():
        v.sort(key=lambda e: (e["layer"], e["name"].lower()))
        (out / (k + ".json")).write_text(json.dumps(v, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print({k: len(v) for k, v in groups.items()}, "total", len(E))


if __name__ == "__main__":
    main()
