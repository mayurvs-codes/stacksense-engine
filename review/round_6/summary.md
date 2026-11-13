# Round 6 engine outputs (auto-generated)

15 scenarios, 0 with oracle violations

### R6-01 [blog_india] status=ok style=static cost=$0-0
- stack: fr=Eleventy | ba=None | da=None | ho=Cloudflare Pages
- supporting: 
- warnings: []
- errors: []
- oracle violations: []

### R6-02 [crm_saas] status=ok style=modular_monolith cost=$72-464
- stack: fr=Blazor | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure Container Apps
- supporting: auth:Microsoft Entra ID, cache:Azure Managed Redis, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R6-03 [rides] status=ok style=service_oriented cost=$443-3165
- stack: fr=React Native (Expo) | ba=Spring Boot | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Centrifugo, payments:Razorpay, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R6-04 [lab_onprem] status=ok style=monolith cost=$0-90
- stack: fr=HTMX with server-rendered templates | ba=Django | da=SQLite | ho=Linux server (systemd + Nginx)
- supporting: auth:Keycloak, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R6-05 [bank_airgap] status=ok_with_warnings style=modular_monolith cost=$18-210
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['SINGLE_VM_AVAILABILITY:warning']
- errors: []
- oracle violations: []

### R6-06 [event_spike] status=ok style=modular_monolith cost=$198-1614
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, search:Meilisearch, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R6-07 [ml_vision] status=ok style=serverless cost=$130-824
- stack: fr=React Native (Expo) | ba=FastAPI | da=Amazon Aurora PostgreSQL | ho=AWS Lambda
- supporting: auth:Amazon Cognito, storage:Amazon S3, ml:Amazon SageMaker, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R6-08 [gdpr_news] status=ok_with_warnings style=modular_monolith cost=$550-3577
- stack: fr=Astro | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, queue:BullMQ, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:critical', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R6-09 [iot_edge] status=ok style=modular_monolith cost=$16-183
- stack: fr=None | ba=Go (Gin) | da=TimescaleDB | ho=Docker Compose on a Linux VM
- supporting: cache:Redis (self-hosted), queue:RabbitMQ, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: ['PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R6-10 [kids_edu] status=ok style=modular_monolith cost=$26-208
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R6-11 [hr_gcp] status=ok style=monolith cost=$11-92
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['LAUNCH_ABOVE_TWELVE_MONTHS:info']
- errors: []
- oracle violations: []

### R6-12 [api_billing] status=ok style=modular_monolith cost=$41-238
- stack: fr=None | ba=Go (Gin) | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: payments:Stripe, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R6-13 [retail_pos] status=ok style=modular_monolith cost=$1-53
- stack: fr=Flutter | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Razorpay, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R6-14 [tiny_all] status=ok_with_warnings style=monolith cost=$0-43
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R6-15 [huge_social] status=ok style=microservices cost=$15763-113588
- stack: fr=React Native (Expo) | ba=Go (Gin) | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Ably, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []
