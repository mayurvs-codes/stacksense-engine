# Round 4 engine outputs (auto-generated)

25 scenarios, 0 with oracle violations

### R4-01 [air_gap_ml] status=ok style=modular_monolith cost=$10-281
- stack: fr=HTMX with server-rendered templates | ba=FastAPI | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, ml:pgvector (PostgreSQL extension), ml:Ollama, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info']
- errors: []
- oracle violations: []

### R4-02 [onprem_k8s] status=ok style=service_oriented cost=$410-3668
- stack: fr=HTMX with server-rendered templates | ba=Go (Gin) | da=PostgreSQL | ho=Kubernetes (k3s) on-prem
- supporting: auth:Keycloak, cache:Redis (self-hosted), queue:RabbitMQ, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R4-03 [pci_only] status=ok style=serverless cost=$22-149
- stack: fr=HTMX with server-rendered templates | ba=Ruby on Rails | da=Amazon RDS for PostgreSQL | ho=AWS Lambda
- supporting: auth:Amazon Cognito, payments:Stripe, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R4-04 [hipaa_india] status=ok style=modular_monolith cost=$93-577
- stack: fr=Kotlin (Jetpack Compose) | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Keycloak, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['PHONE_OTP_CUSTOM:info']
- errors: []
- oracle violations: []

### R4-05 [other_residency] status=ok_with_warnings style=modular_monolith cost=$30-186
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['RESIDENCY_OTHER:warning']
- errors: []
- oracle violations: []

### R4-06 [azure_none] status=ok style=modular_monolith cost=$22-167
- stack: fr=HTMX with server-rendered templates | ba=ASP.NET Core | da=PostgreSQL | ho=DigitalOcean Droplets
- supporting: auth:ASP.NET Core Identity, ci_cd:GitHub Actions, observability:Sentry
- warnings: []
- errors: []
- oracle violations: []

### R4-07 [gcp_dpdp_pay] status=ok style=modular_monolith cost=$113-990
- stack: fr=Next.js | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Socket.IO, payments:Razorpay, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-08 [tiny_ios] status=ok_with_warnings style=serverless cost=$0-32
- stack: fr=Swift (SwiftUI) | ba=Django | da=Supabase Postgres | ho=AWS Lambda
- supporting: auth:Firebase Authentication, ci_cd:AWS CodePipeline
- warnings: ['BUDGET_EXCEEDED:warning', 'SKILL_MISMATCH:warning', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R4-09 [desktop_cross] status=ok style=modular_monolith cost=$30-186
- stack: fr=Electron | ba=NestJS | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R4-10 [huge_static] status=ok style=static cost=$0-36
- stack: fr=Astro | ba=None | da=None | ho=Cloudflare Pages
- supporting: 
- warnings: []
- errors: []
- oracle violations: []

### R4-11 [avail_senior] status=ok style=modular_monolith cost=$373-2393
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-12 [timeline_ok] status=ok style=monolith cost=$11-80
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-13 [sap_existing] status=ok style=modular_monolith cost=$19-117
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Microsoft Entra ID, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R4-14 [mongo_existing] status=ok_with_warnings style=modular_monolith cost=$14-160
- stack: fr=Next.js | ba=NestJS | da=MongoDB Atlas | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['EOL_EXISTING_SYSTEM:warning']
- errors: []
- oracle violations: []

### R4-15 [mysql8] status=ok style=modular_monolith cost=$10-139
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=MySQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-16 [gdpr_sens] status=ok style=modular_monolith cost=$22-160
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-17 [rps_big] status=ok style=modular_monolith cost=$107-639
- stack: fr=None | ba=Go (Gin) | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-18 [hiring] status=ok style=serverless cost=$508-3347
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Amazon RDS for PostgreSQL | ho=AWS Lambda
- supporting: auth:Amazon Cognito, cache:Amazon ElastiCache, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R4-19 [licences] status=ok style=modular_monolith cost=$20-121
- stack: fr=HTMX with server-rendered templates | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Microsoft Entra ID, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R4-20 [integr] status=ok style=modular_monolith cost=$65-423
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-21 [offline_sync_merge] status=ok style=modular_monolith cost=$2-67
- stack: fr=React Native (Expo) | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R4-22 [realtime_tiny] status=ok_with_warnings style=monolith cost=$0-46
- stack: fr=React (Vite) | ba=Express | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Socket.IO, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_EXCEEDED:warning', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R4-23 [analytics_ondemand] status=ok style=modular_monolith cost=$30-294
- stack: fr=HTMX with server-rendered templates | ba=Django | da=ClickHouse | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R4-24 [emptyish] status=ok_with_warnings style=monolith cost=$0-36
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R4-25 [all_flags] status=ok_with_warnings style=service_oriented cost=$1483-9515
- stack: fr=React Native (Expo) | ba=NestJS | da=Amazon RDS for PostgreSQL | ho=AWS ECS on Fargate
- supporting: auth:Amazon Cognito, storage:Amazon S3, realtime:Centrifugo, payments:Stripe, ml:Amazon SageMaker, search:Meilisearch, cache:Amazon ElastiCache, queue:Amazon SQS, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['OFFLINE_SYNC_CUSTOM:warning', 'SEO_LIMITATION:warning']
- errors: []
- oracle violations: []
