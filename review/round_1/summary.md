# Round 1 engine outputs (auto-generated)

32 scenarios, 0 with oracle violations

### R1-01 [invalid] status=invalid_input style=other cost=$0-0
- stack: -
- supporting: -
- warnings: []
- errors: ['project.type', 'team.size']
- oracle violations: []

### R1-02 [invalid] status=invalid_input style=other cost=$0-0
- stack: -
- supporting: -
- warnings: []
- errors: ['scale.users_12_months', 'budget.monthly_infra_usd', 'priorities.cost']
- oracle violations: []

### R1-03 [invalid] status=invalid_input style=other cost=$0-0
- stack: -
- supporting: -
- warnings: []
- errors: ['team.languages', 'infrastructure.deployment_model']
- oracle violations: []

### R1-04 [contradiction] status=ok_with_warnings style=modular_monolith cost=$12010-80485
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:critical', 'SCALE_VS_BUDGET:critical', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R1-05 [contradiction] status=ok_with_warnings style=serverless cost=$8-120
- stack: fr=React (Vite) | ba=Django | da=Supabase Postgres | ho=AWS Lambda
- supporting: auth:Firebase Authentication, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['AVAILABILITY_VS_TEAM:critical', 'BUDGET_EXCEEDED:warning']
- errors: []
- oracle violations: []

### R1-06 [contradiction] status=ok_with_warnings style=monolith cost=$30-195
- stack: fr=Flutter | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['TIMELINE_VS_PLATFORMS:warning']
- errors: []
- oracle violations: []

### R1-07 [overengineering] status=ok_with_warnings style=static cost=$0-10
- stack: fr=Astro | ba=None | da=None | ho=Cloudflare Pages
- supporting: 
- warnings: ['SCALE_VS_BUDGET:warning']
- errors: []
- oracle violations: []

### R1-08 [overengineering] status=ok style=monolith cost=$0-42
- stack: fr=HTMX with server-rendered templates | ba=Django | da=SQLite | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R1-09 [overengineering] status=ok style=monolith cost=$0-74
- stack: fr=React (Vite) | ba=Django | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R1-10 [regulated] status=ok style=modular_monolith cost=$23-192
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-11 [regulated] status=ok style=modular_monolith cost=$21-184
- stack: fr=Blazor | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure Container Apps
- supporting: auth:ASP.NET Core Identity, payments:Razorpay, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R1-12 [regulated] status=ok style=modular_monolith cost=$22-182
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, payments:Stripe, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-13 [regulated] status=ok style=service_oriented cost=$508-4466
- stack: fr=Next.js | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, cache:Google Cloud Memorystore, queue:BullMQ, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-14 [legacy] status=ok_with_warnings style=modular_monolith cost=$30-195
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['EOL_EXISTING_SYSTEM:warning', 'EOL_EXISTING_SYSTEM:warning', 'EOL_EXISTING_SYSTEM:warning']
- errors: []
- oracle violations: []

### R1-15 [legacy] status=ok_with_warnings style=modular_monolith cost=$30-182
- stack: fr=Blazor | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:ASP.NET Core Identity, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['EOL_EXISTING_SYSTEM:warning', 'EOL_EXISTING_SYSTEM:warning']
- errors: []
- oracle violations: []

### R1-16 [restricted] status=ok style=modular_monolith cost=$14-202
- stack: fr=Next.js | ba=Django | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, storage:SeaweedFS, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R1-17 [restricted] status=ok style=modular_monolith cost=$50-482
- stack: fr=Next.js | ba=NestJS | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, realtime:Socket.IO, cache:Redis (self-hosted), ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R1-18 [restricted] status=ok style=modular_monolith cost=$28-186
- stack: fr=Next.js | ba=Django | da=PostgreSQL | ho=AWS EC2
- supporting: auth:Amazon Cognito, payments:Stripe, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R1-19 [skill] status=ok style=modular_monolith cost=$30-195
- stack: fr=None | ba=Axum | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R1-20 [skill] status=ok_with_warnings style=modular_monolith cost=$30-195
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['SKILL_MISMATCH:warning']
- errors: []
- oracle violations: []

### R1-21 [offline] status=ok style=monolith cost=$9-136
- stack: fr=Kotlin (Jetpack Compose) | ba=Ktor | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R1-22 [offline] status=ok style=modular_monolith cost=$14-171
- stack: fr=React Native (Expo) | ba=Spring Boot | da=CouchDB | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R1-23 [realtime_scale] status=ok style=service_oriented cost=$3013-26619
- stack: fr=SvelteKit | ba=Go (Gin) | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Ably, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-24 [realtime_scale] status=ok style=modular_monolith cost=$23-207
- stack: fr=Next.js | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Yjs, cache:Google Cloud Memorystore, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-25 [ml] status=ok style=modular_monolith cost=$56-582
- stack: fr=HTMX with server-rendered templates | ba=FastAPI | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ml:pgvector (PostgreSQL extension), ml:Google Vertex AI, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R1-26 [ml] status=ok style=modular_monolith cost=$14-328
- stack: fr=HTMX with server-rendered templates | ba=FastAPI | da=PostgreSQL | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, ml:PyTorch, queue:RabbitMQ, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []

### R1-27 [extreme_budget] status=ok_with_warnings style=monolith cost=$0-28
- stack: fr=React (Vite) | ba=Express | da=SQLite | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R1-28 [extreme_budget] status=ok style=microservices cost=$40013-284976
- stack: fr=Next.js | ba=Spring Boot | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, realtime:Ably, payments:Stripe, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R1-29 [minimal] status=ok style=monolith cost=$19-110
- stack: fr=HTMX with server-rendered templates | ba=Laravel | da=Azure SQL Database | ho=Azure App Service
- supporting: ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R1-30 [minimal] status=ok style=modular_monolith cost=$18-107
- stack: fr=HTMX with server-rendered templates | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure App Service
- supporting: ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R1-31 [extras] status=ok_with_warnings style=modular_monolith cost=$758-4920
- stack: fr=Next.js | ba=NestJS | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Auth0, storage:Google Cloud Storage, payments:Stripe, cache:Google Cloud Memorystore, queue:BullMQ, cdn:Google Cloud CDN, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'OPTIONAL_COMPONENT_DEFERRED:info', 'SENSITIVE_DATA_NO_COMPLIANCE:info']
- errors: []
- oracle violations: []

### R1-32 [extras] status=ok_with_warnings style=modular_monolith cost=$30-195
- stack: fr=React Native (Expo) | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['OFFLINE_SYNC_CUSTOM:warning', 'SYNC_CONSISTENCY:warning', 'LICENCE_NOT_USED:info', 'SENSITIVE_DATA_NO_COMPLIANCE:info']
- errors: []
- oracle violations: []
