# Knowledge-base audit

Generated 2026-11-13 by `tools/gen_kb_audit.py` from `data/kb/*.json`, `tools/verified.json` (written by `tools/verify_sources.py`) and `tools/github_lifecycle.json` (GitHub API check of open-source projects).

## What was verified, honestly

- **Source pages opened.** Every source URL in the KB was fetched on the date shown in its `accessed` field and returned HTTP 200 with real HTML (a few URLs that returned 404/403 on the first pass were corrected and re-checked; `dev.mysql.com` blocks scripted clients, so it was opened in the browser pane instead). Opening a page proves the product page exists, not every claim made about the product.
- **Region claims opened and read** (official pages, 2026-11-13): AWS regions list (Mumbai ap-south-1, Hyderabad ap-south-2, Frankfurt, Ireland, ...); Azure regions list (Central India/Pune, India South Central/Hyderabad, South India/Chennai, West India/Mumbai); Google Compute Engine regions (Mumbai asia-south1, Delhi asia-south2); DigitalOcean regional availability (BLR1 Bangalore, FRA1, AMS3, NYC, SFO); Vercel regions (bom1 Mumbai); Render regions (Oregon, Ohio, Virginia, Frankfurt, Singapore: no India region); Supabase regions (Mumbai, Frankfurt, Ireland, London, Zurich); Firestore locations (asia-south1 Mumbai, eur3, europe-* locations); MongoDB Atlas on AWS (Hyderabad ap-south-2).
- **Not verified this run (stated as such, kept conservative):** EU/US region availability of Azure, Google Cloud, Vercel and MongoDB Atlas (general knowledge, widely published); vendor compliance attestations (PCI DSS, HIPAA, SOC 2, ISO 27001 for AWS/Azure/GCP and PCI DSS for the payment gateways) come from public compliance programmes but their pages were not read claim by claim; Fly.io, Railway, Netlify, Cloudflare and Hetzner region claims were NOT used (Fly page showed no India region, Hetzner's docs failed TLS verification, Railway not checked), so these have no India/EU/US region claims and are never chosen under data residency (Hetzner and Fly.io are not in the KB).
- **Lifecycle.** Open-source projects were checked through the GitHub API on 2026-11-13: none is archived and every repository received commits within the last six weeks (see table). The check removed **MinIO**: its open-source repository's README states it is no longer maintained, so it was replaced by SeaweedFS. `dotnet/blazor` is archived because Blazor now lives inside `dotnet/aspnetcore`; htmx moved organisations.
- **Ratings and costs are author judgements.** The 1-5 ratings and the USD cost bands are curated estimates informed by the cited pricing and documentation pages; they are not vendor quotes and not benchmark results. They are documented as such in the report.
- **Timescale** has rebranded its documentation site to "Tiger Data"; TimescaleDB remains an active product.

## Entries

| Layer | Entry | Source pages opened | OSS lifecycle check |
|---|---|---|---|
| auth | Amazon Cognito | [Amazon Cognito](https://aws.amazon.com/cognito/) (2026-11-13) | n/a (commercial/managed service or standard) |
| auth | ASP.NET Core Identity | [ASP.NET Core Identity](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity) (2026-11-13) | n/a (commercial/managed service or standard) |
| auth | Auth0 | [Auth0 docs](https://auth0.com/docs) (2026-11-13) | n/a (commercial/managed service or standard) |
| auth | Firebase Authentication | [Firebase Authentication](https://firebase.google.com/docs/auth) (2026-11-13) | n/a (commercial/managed service or standard) |
| auth | Keycloak | [Keycloak docs](https://www.keycloak.org/documentation) (2026-11-13) | keycloak/keycloak: archived=False, last push 2026-11-13 |
| auth | Microsoft Entra ID | [What is Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis) (2026-11-13) | n/a (commercial/managed service or standard) |
| backend | ASP.NET Core | [ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/introduction-to-aspnet-core) (2026-11-13) | dotnet/aspnetcore: archived=False, last push 2026-11-13 |
| backend | Axum | [Axum docs](https://docs.rs/axum/latest/axum/) (2026-11-13) | tokio-rs/axum: archived=False, last push 2026-11-12 |
| backend | Django | [Django docs](https://docs.djangoproject.com/en/stable/) (2026-11-13) | django/django: archived=False, last push 2026-11-13 |
| backend | Express | [Express](https://expressjs.com/) (2026-11-13) | expressjs/express: archived=False, last push 2026-11-02 |
| backend | FastAPI | [FastAPI](https://fastapi.tiangolo.com/) (2026-11-13) | tiangolo/fastapi: archived=False, last push 2026-11-11 |
| backend | Go (Gin) | [Gin docs](https://gin-gonic.com/) (2026-11-13) | gin-gonic/gin: archived=False, last push 2026-10-10 |
| backend | Ktor | [Ktor docs](https://ktor.io/docs/welcome.html) (2026-11-13) | ktorio/ktor: archived=False, last push 2026-11-12 |
| backend | Laravel | [Laravel docs](https://laravel.com/docs) (2026-11-13) | laravel/framework: archived=False, last push 2026-11-12 |
| backend | NestJS | [NestJS docs](https://docs.nestjs.com/) (2026-11-13) | nestjs/nest: archived=False, last push 2026-11-13 |
| backend | Ruby on Rails | [Rails Guides](https://guides.rubyonrails.org/) (2026-11-13) | rails/rails: archived=False, last push 2026-11-13 |
| backend | Spring Boot | [Spring Boot](https://spring.io/projects/spring-boot) (2026-11-13) | spring-projects/spring-boot: archived=False, last push 2026-11-13 |
| cache | Amazon ElastiCache | [Amazon ElastiCache](https://aws.amazon.com/elasticache/) (2026-11-13) | n/a (commercial/managed service or standard) |
| cache | Google Cloud Memorystore | [Memorystore docs](https://cloud.google.com/memorystore/docs) (2026-11-13) | n/a (commercial/managed service or standard) |
| cache | Redis (self-hosted) | [Redis docs](https://redis.io/docs/latest/) (2026-11-13) | redis/redis: archived=False, last push 2026-11-12 |
| cache | Valkey (self-hosted) | [Valkey](https://valkey.io/) (2026-11-13) | valkey-io/valkey: archived=False, last push 2026-11-13 |
| cdn | Amazon CloudFront | [Amazon CloudFront](https://aws.amazon.com/cloudfront/) (2026-11-13) | n/a (commercial/managed service or standard) |
| cdn | Azure Front Door | [Azure Front Door](https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| cdn | Cloudflare CDN | [Cloudflare Cache docs](https://developers.cloudflare.com/cache/) (2026-11-13) | n/a (commercial/managed service or standard) |
| cdn | Google Cloud CDN | [Cloud CDN overview](https://cloud.google.com/cdn/docs/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | AWS CodePipeline | [AWS CodePipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | Azure DevOps Pipelines | [Azure Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | GitHub Actions | [GitHub Actions docs](https://docs.github.com/en/actions) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | GitLab CI/CD (self-managed) | [GitLab CI/CD docs](https://docs.gitlab.com/ee/ci/) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | Google Cloud Build | [Cloud Build overview](https://cloud.google.com/build/docs/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| ci_cd | Jenkins | [Jenkins docs](https://www.jenkins.io/doc/) (2026-11-13) | jenkinsci/jenkins: archived=False, last push 2026-11-12 |
| database | Amazon Aurora PostgreSQL | [Amazon Aurora](https://aws.amazon.com/rds/aurora/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Amazon DynamoDB | [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Amazon RDS for PostgreSQL | [Amazon RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Azure Database for PostgreSQL | [Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Azure SQL Database | [Azure SQL Database](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | ClickHouse | [ClickHouse intro](https://clickhouse.com/docs/en/intro) (2026-11-13) | ClickHouse/ClickHouse: archived=False, last push 2026-11-13 |
| database | CouchDB | [CouchDB overview](https://docs.couchdb.org/en/stable/intro/overview.html) (2026-11-13) | apache/couchdb: archived=False, last push 2026-11-13 |
| database | Firestore | [Firestore locations](https://firebase.google.com/docs/firestore/locations) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Google Cloud SQL for PostgreSQL | [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Microsoft SQL Server | [SQL Server docs](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2022) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | MongoDB Atlas | [Atlas on AWS regions](https://www.mongodb.com/docs/atlas/reference/amazon-aws/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | MySQL | [MySQL Community Edition](https://dev.mysql.com/doc/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | PostgreSQL | [About PostgreSQL](https://www.postgresql.org/about/) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | SQLite | [About SQLite](https://www.sqlite.org/about.html) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | Supabase Postgres | [Supabase regions](https://supabase.com/docs/guides/platform/regions) (2026-11-13) | n/a (commercial/managed service or standard) |
| database | TimescaleDB | [Timescale docs](https://docs.timescale.com/) (2026-11-13) | timescale/timescaledb: archived=False, last push 2026-11-13 |
| frontend | Angular | [Angular overview](https://angular.dev/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Astro | [Why Astro](https://docs.astro.build/en/concepts/why-astro/) (2026-11-13) | withastro/astro: archived=False, last push 2026-11-13 |
| frontend | Blazor | [Blazor overview](https://learn.microsoft.com/en-us/aspnet/core/blazor/) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Electron | [Electron docs](https://www.electronjs.org/docs/latest/) (2026-11-13) | electron/electron: archived=False, last push 2026-11-13 |
| frontend | Eleventy | [Eleventy docs](https://www.11ty.dev/docs/) (2026-11-13) | 11ty/eleventy: archived=False, last push 2026-11-12 |
| frontend | Flutter | [Flutter docs](https://docs.flutter.dev/) (2026-11-13) | flutter/flutter: archived=False, last push 2026-11-13 |
| frontend | HTMX with server-rendered templates | [htmx docs](https://htmx.org/docs/) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Kotlin (Jetpack Compose) | [Jetpack Compose](https://developer.android.com/compose) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Next.js | [Next.js docs](https://nextjs.org/docs) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Nuxt | [Nuxt docs](https://nuxt.com/docs) (2026-11-13) | nuxt/nuxt: archived=False, last push 2026-11-13 |
| frontend | React (Vite) | [React](https://react.dev/) (2026-11-13); [Vite guide](https://vite.dev/guide/) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | React Native (Expo) | [Expo docs](https://docs.expo.dev/) (2026-11-13) | expo/expo: archived=False, last push 2026-11-13 |
| frontend | SvelteKit | [SvelteKit docs](https://svelte.dev/docs/kit) (2026-11-13) | sveltejs/kit: archived=False, last push 2026-11-12 |
| frontend | Swift (SwiftUI) | [SwiftUI](https://developer.apple.com/swiftui/) (2026-11-13) | n/a (commercial/managed service or standard) |
| frontend | Tauri | [Tauri docs](https://tauri.app/start/) (2026-11-13) | tauri-apps/tauri: archived=False, last push 2026-11-12 |
| hosting | AWS Amplify Hosting | [AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | AWS EC2 | [Amazon EC2](https://aws.amazon.com/ec2/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | AWS ECS on Fargate | [AWS Fargate](https://aws.amazon.com/fargate/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | AWS Lambda | [AWS Lambda](https://aws.amazon.com/lambda/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Azure App Service | [Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Azure Container Apps | [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Azure Static Web Apps | [Azure Static Web Apps](https://learn.microsoft.com/en-us/azure/static-web-apps/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Azure Virtual Machines | [Azure Virtual Machines](https://learn.microsoft.com/en-us/azure/virtual-machines/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Cloudflare Pages | [Cloudflare Pages](https://developers.cloudflare.com/pages/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | DigitalOcean Droplets | [DigitalOcean regional availability](https://docs.digitalocean.com/platform/regional-availability/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Docker Compose on a Linux VM | [Docker Compose](https://docs.docker.com/compose/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | GitHub Pages | [About GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Google Cloud Run | [What is Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Google Compute Engine | [Compute Engine regions and zones](https://docs.cloud.google.com/compute/docs/regions-zones) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Kubernetes (k3s) on-prem | [K3s documentation](https://docs.k3s.io/) (2026-11-13) | k3s-io/k3s: archived=False, last push 2026-11-12 |
| hosting | Linux server (systemd + Nginx) | [nginx documentation](https://nginx.org/en/docs/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Netlify | [Netlify docs](https://docs.netlify.com/) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Render | [Render regions](https://render.com/docs/regions) (2026-11-13) | n/a (commercial/managed service or standard) |
| hosting | Vercel | [Vercel regions](https://vercel.com/docs/regions) (2026-11-13) | n/a (commercial/managed service or standard) |
| ml | Amazon SageMaker | [Amazon SageMaker](https://aws.amazon.com/sagemaker/) (2026-11-13) | n/a (commercial/managed service or standard) |
| ml | Azure Machine Learning | [What is Azure Machine Learning](https://learn.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-machine-learning) (2026-11-13) | n/a (commercial/managed service or standard) |
| ml | Google Vertex AI | [Vertex AI introduction](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform) (2026-11-13) | n/a (commercial/managed service or standard) |
| ml | Ollama | [Ollama](https://github.com/ollama/ollama) (2026-11-13) | ollama/ollama: archived=False, last push 2026-11-13 |
| ml | ONNX Runtime | [ONNX Runtime docs](https://onnxruntime.ai/docs/) (2026-11-13) | n/a (commercial/managed service or standard) |
| ml | pgvector (PostgreSQL extension) | [pgvector](https://github.com/pgvector/pgvector) (2026-11-13) | pgvector/pgvector: archived=False, last push 2026-11-13 |
| ml | Qdrant | [Qdrant docs](https://qdrant.tech/documentation/) (2026-11-13) | qdrant/qdrant: archived=False, last push 2026-11-13 |
| ml | scikit-learn (self-hosted inference) | [scikit-learn](https://scikit-learn.org/stable/) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Amazon CloudWatch | [What is CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Azure Monitor | [Azure Monitor overview](https://learn.microsoft.com/en-us/azure/azure-monitor/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Datadog | [Datadog docs](https://docs.datadoghq.com/) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Google Cloud Operations Suite | [Google Cloud Observability](https://cloud.google.com/products/operations) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Grafana + Prometheus | [Prometheus overview](https://prometheus.io/docs/introduction/overview/) (2026-11-13); [Grafana docs](https://grafana.com/docs/grafana/latest/) (2026-11-13) | grafana/grafana: archived=False, last push 2026-11-13 |
| observability | Sentry | [Sentry docs](https://docs.sentry.io/) (2026-11-13) | n/a (commercial/managed service or standard) |
| observability | Sentry (self-hosted) | [Sentry self-hosted](https://develop.sentry.dev/self-hosted/) (2026-11-13) | getsentry/self-hosted: archived=False, last push 2026-11-13 |
| payments | Adyen | [Adyen docs](https://docs.adyen.com/) (2026-11-13) | n/a (commercial/managed service or standard) |
| payments | Cashfree Payments | [Cashfree docs](https://docs.cashfree.com/) (2026-11-13) | n/a (commercial/managed service or standard) |
| payments | PayU | [PayU docs](https://docs.payu.in/) (2026-11-13) | n/a (commercial/managed service or standard) |
| payments | Razorpay | [Razorpay docs](https://razorpay.com/docs/) (2026-11-13) | n/a (commercial/managed service or standard) |
| payments | Stripe | [Stripe docs](https://docs.stripe.com/) (2026-11-13) | n/a (commercial/managed service or standard) |
| queue | Amazon SQS | [Amazon SQS](https://aws.amazon.com/sqs/) (2026-11-13) | n/a (commercial/managed service or standard) |
| queue | Apache Kafka | [Kafka documentation](https://kafka.apache.org/documentation/) (2026-11-13) | apache/kafka: archived=False, last push 2026-11-12 |
| queue | Azure Service Bus | [Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| queue | BullMQ | [BullMQ docs](https://docs.bullmq.io/) (2026-11-13) | taskforcesh/bullmq: archived=False, last push 2026-11-13 |
| queue | Google Cloud Pub/Sub | [Pub/Sub overview](https://cloud.google.com/pubsub/docs/overview) (2026-11-13) | n/a (commercial/managed service or standard) |
| queue | RabbitMQ | [RabbitMQ docs](https://www.rabbitmq.com/docs) (2026-11-13) | rabbitmq/rabbitmq-server: archived=False, last push 2026-11-13 |
| realtime | Ably | [Ably docs](https://ably.com/docs) (2026-11-13) | n/a (commercial/managed service or standard) |
| realtime | Centrifugo | [Centrifugo introduction](https://centrifugal.dev/docs/getting-started/introduction) (2026-11-13) | centrifugal/centrifugo: archived=False, last push 2026-11-11 |
| realtime | Pusher Channels | [Pusher Channels docs](https://pusher.com/docs/channels/) (2026-11-13) | n/a (commercial/managed service or standard) |
| realtime | Socket.IO | [Socket.IO docs](https://socket.io/docs/v4/) (2026-11-13) | socketio/socket.io: archived=False, last push 2026-11-13 |
| realtime | Yjs | [Yjs docs](https://docs.yjs.dev/) (2026-11-13) | yjs/yjs: archived=False, last push 2026-11-09 |
| search | Algolia | [Algolia docs](https://www.algolia.com/doc/) (2026-11-13) | n/a (commercial/managed service or standard) |
| search | Meilisearch | [Meilisearch docs](https://www.meilisearch.com/docs) (2026-11-13) | meilisearch/meilisearch: archived=False, last push 2026-11-12 |
| search | OpenSearch | [OpenSearch docs](https://opensearch.org/docs/latest/) (2026-11-13) | opensearch-project/OpenSearch: archived=False, last push 2026-11-12 |
| search | Typesense | [Typesense docs](https://typesense.org/docs/) (2026-11-13) | typesense/typesense: archived=False, last push 2026-11-11 |
| storage | Amazon S3 | [Amazon S3](https://aws.amazon.com/s3/) (2026-11-13) | n/a (commercial/managed service or standard) |
| storage | Azure Blob Storage | [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) (2026-11-13) | n/a (commercial/managed service or standard) |
| storage | Cloudflare R2 | [Cloudflare R2](https://developers.cloudflare.com/r2/) (2026-11-13) | n/a (commercial/managed service or standard) |
| storage | Google Cloud Storage | [Cloud Storage introduction](https://cloud.google.com/storage/docs/introduction) (2026-11-13) | n/a (commercial/managed service or standard) |
| storage | SeaweedFS | [SeaweedFS repository](https://github.com/seaweedfs/seaweedfs) (2026-11-13) | seaweedfs/seaweedfs: archived=False, last push 2026-11-13 |
