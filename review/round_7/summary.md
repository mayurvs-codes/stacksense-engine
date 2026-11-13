# Round 7 engine outputs (auto-generated)

15 scenarios, 0 with oracle violations

### R7-01 [gcp_eu_health] status=ok style=modular_monolith cost=$107-705
- stack: fr=Next.js | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Keycloak, realtime:Centrifugo, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R7-02 [aws_vm_lowlock] status=ok style=modular_monolith cost=$38-240
- stack: fr=HTMX with server-rendered templates | ba=Django | da=PostgreSQL | ho=AWS EC2
- supporting: auth:Keycloak, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R7-03 [azure_india_rbi] status=ok style=modular_monolith cost=$378-2281
- stack: fr=Blazor | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure Container Apps
- supporting: auth:ASP.NET Core Identity, payments:Razorpay, cache:Azure Managed Redis, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['PHONE_OTP_CUSTOM:info']
- errors: []
- oracle violations: []

### R7-04 [static_docs_onprem] status=ok style=static cost=$0-67
- stack: fr=Astro | ba=None | da=None | ho=Linux server (systemd + Nginx)
- supporting: search:Meilisearch, ci_cd:GitLab CI/CD (self-managed)
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R7-05 [mobile_only_ios_offline] status=ok_with_warnings style=monolith cost=$7-110
- stack: fr=Swift (SwiftUI) | ba=Django | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['SKILL_MISMATCH:warning']
- errors: []
- oracle violations: []

### R7-06 [game_backend_only] status=ok style=service_oriented cost=$2083-12803
- stack: fr=None | ba=Go (Gin) | da=Amazon DynamoDB | ho=AWS ECS on Fargate
- supporting: auth:Amazon Cognito, realtime:Ably, cache:Amazon ElastiCache, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R7-07 [ngo_forms] status=ok_with_warnings style=monolith cost=$2-50
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Supabase Postgres | ho=Google Cloud Run
- supporting: storage:Google Cloud Storage, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R7-08 [enterprise_lowlock_sens] status=ok style=modular_monolith cost=$198-1321
- stack: fr=Next.js | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Keycloak, cache:Google Cloud Memorystore, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R7-09 [legacy_php] status=ok_with_warnings style=modular_monolith cost=$28-200
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['EOL_EXISTING_SYSTEM:warning', 'EOL_EXISTING_SYSTEM:warning']
- errors: []
- oracle violations: []

### R7-10 [k8s_ok_team] status=ok style=service_oriented cost=$610-5170
- stack: fr=None | ba=Spring Boot | da=PostgreSQL | ho=Kubernetes (k3s) on-prem
- supporting: cache:Redis (self-hosted), queue:RabbitMQ, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R7-11 [ml_llm_india] status=ok style=modular_monolith cost=$80-758
- stack: fr=HTMX with server-rendered templates | ba=FastAPI | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ml:pgvector (PostgreSQL extension), ml:Google Vertex AI, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R7-12 [desktop_pos_offline] status=ok style=modular_monolith cost=$0-41
- stack: fr=Flutter | ba=ASP.NET Core | da=Firestore | ho=Google Cloud Run
- supporting: auth:ASP.NET Core Identity, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info']
- errors: []
- oracle violations: []

### R7-13 [spiky_ticket_cheap] status=ok style=serverless cost=$40-440
- stack: fr=Next.js | ba=NestJS | da=Supabase Postgres | ho=AWS Lambda
- supporting: auth:Amazon Cognito, payments:Stripe, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['BUDGET_UPPER_BAND:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R7-14 [cloudnone_air] status=ok style=modular_monolith cost=$14-222
- stack: fr=Next.js | ba=Spring Boot | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, realtime:Centrifugo, cache:Redis (self-hosted), ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R7-15 [everything_india_vm] status=ok style=modular_monolith cost=$96-632
- stack: fr=Next.js | ba=NestJS | da=PostgreSQL | ho=AWS EC2
- supporting: auth:Amazon Cognito, storage:Amazon S3, realtime:Socket.IO, payments:Razorpay, cache:Amazon ElastiCache, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []
