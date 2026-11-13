# Round 2 engine outputs (auto-generated)

25 scenarios, 0 with oracle violations

### R2-01 [hobby] status=ok style=static cost=$0-0
- stack: fr=Eleventy | ba=None | da=None | ho=Cloudflare Pages
- supporting: 
- warnings: []
- errors: []
- oracle violations: []

### R2-02 [india_shop] status=ok style=modular_monolith cost=$36-277
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, payments:Razorpay, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R2-03 [saas_india] status=ok style=modular_monolith cost=$28-199
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-04 [telemedicine] status=ok style=modular_monolith cost=$83-562
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Socket.IO, cache:Google Cloud Memorystore, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-05 [iot_fleet] status=ok style=modular_monolith cost=$40-197
- stack: fr=HTMX with server-rendered templates | ba=Go (Gin) | da=TimescaleDB | ho=AWS EC2
- supporting: auth:Amazon Cognito, cache:Amazon ElastiCache, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R2-06 [video] status=ok style=service_oriented cost=$1113-10036
- stack: fr=React Native (Expo) | ba=Go (Gin) | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-07 [api_perf] status=ok style=modular_monolith cost=$93-577
- stack: fr=None | ba=Go (Gin) | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-08 [erp] status=ok style=modular_monolith cost=$19-113
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Microsoft Entra ID, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info']
- errors: []
- oracle violations: []

### R2-09 [gov_airgap] status=ok style=modular_monolith cost=$10-176
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, storage:SeaweedFS, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R2-10 [chat] status=ok style=modular_monolith cost=$288-2452
- stack: fr=React Native (Expo) | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Socket.IO, cache:Google Cloud Memorystore, queue:BullMQ, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-11 [edtech_llm] status=ok style=serverless cost=$106-884
- stack: fr=Next.js | ba=FastAPI | da=Amazon RDS for PostgreSQL | ho=AWS Lambda
- supporting: auth:Amazon Cognito, ml:pgvector (PostgreSQL extension), ml:Amazon SageMaker, cache:Amazon ElastiCache, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R2-12 [fintech_eu] status=ok style=modular_monolith cost=$243-1471
- stack: fr=Blazor | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure Container Apps
- supporting: auth:ASP.NET Core Identity, payments:Stripe, cache:Azure Managed Redis, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R2-13 [game_lb] status=ok style=service_oriented cost=$463-4914
- stack: fr=React Native (Expo) | ba=ASP.NET Core | da=Firestore | ho=Google Cloud Run
- supporting: auth:ASP.NET Core Identity, realtime:Centrifugo, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-14 [ngo] status=ok style=serverless cost=$1-53
- stack: fr=Next.js | ba=Express | da=Supabase Postgres | ho=AWS Lambda
- supporting: payments:Stripe, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R2-15 [desktop_offline] status=ok style=modular_monolith cost=$0-48
- stack: fr=Tauri | ba=Express | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info']
- errors: []
- oracle violations: []

### R2-16 [bi] status=ok style=modular_monolith cost=$38-256
- stack: fr=HTMX with server-rendered templates | ba=Django | da=ClickHouse | ho=AWS EC2
- supporting: auth:Amazon Cognito, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R2-17 [gcp_market] status=ok style=modular_monolith cost=$203-1296
- stack: fr=React Native (Expo) | ba=Django | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Ably, payments:Stripe, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-18 [solo_mvp] status=ok_with_warnings style=monolith cost=$1-51
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_EXCEEDED:warning']
- errors: []
- oracle violations: []

### R2-19 [modernize] status=ok style=modular_monolith cost=$55-558
- stack: fr=Next.js | ba=NestJS | da=PostgreSQL | ho=Google Cloud Run
- supporting: auth:Auth0, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-20 [lockin_low] status=ok style=modular_monolith cost=$107-709
- stack: fr=HTMX with server-rendered templates | ba=Go (Gin) | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, cache:Google Cloud Memorystore, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-21 [health_india] status=ok style=modular_monolith cost=$39-300
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-22 [ticketing] status=ok style=service_oriented cost=$513-4398
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Razorpay, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R2-23 [wiki] status=ok style=monolith cost=$10-173
- stack: fr=HTMX with server-rendered templates | ba=Django | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, storage:SeaweedFS, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R2-24 [kiosk] status=ok style=monolith cost=$0-40
- stack: fr=React Native (Expo) | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R2-25 [ml_train] status=ok style=modular_monolith cost=$44-491
- stack: fr=HTMX with server-rendered templates | ba=FastAPI | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ml:Google Vertex AI, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []
