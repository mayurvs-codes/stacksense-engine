# Round 8 engine outputs (auto-generated)

15 scenarios, 0 with oracle violations

### R8-01 [P1_budget_up] status=ok style=monolith cost=$20-118
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, cdn:Cloudflare CDN, ci_cd:Azure DevOps Pipelines
- warnings: []
- errors: []
- oracle violations: []

### R8-02 [P1_eu_gdpr] status=ok style=static cost=$0-0
- stack: fr=Eleventy | ba=None | da=None | ho=GitHub Pages
- supporting: search:Pagefind
- warnings: []
- errors: []
- oracle violations: []

### R8-03 [P2_budget_x10] status=ok_with_warnings style=modular_monolith cost=$208-1604
- stack: fr=React Native (Expo) | ba=NestJS | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Socket.IO, payments:Razorpay, cache:Google Cloud Memorystore, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['SEO_LIMITATION:warning', 'BUDGET_UPPER_BAND:info']
- errors: []
- oracle violations: []

### R8-04 [P2_no_residency] status=ok_with_warnings style=modular_monolith cost=$16-194
- stack: fr=React Native (Expo) | ba=NestJS | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Socket.IO, payments:Stripe, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['SEO_LIMITATION:warning', 'BUDGET_UPPER_BAND:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R8-05 [P2_aws_pinned] status=ok_with_warnings style=modular_monolith cost=$28-220
- stack: fr=React Native (Expo) | ba=Spring Boot | da=Supabase Postgres | ho=AWS EC2
- supporting: auth:Amazon Cognito, storage:Amazon S3, realtime:Centrifugo, payments:Razorpay, ci_cd:AWS CodePipeline
- warnings: ['SEO_LIMITATION:warning', 'BUDGET_UPPER_BAND:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R8-06 [P3_india] status=ok style=modular_monolith cost=$60-549
- stack: fr=Next.js | ba=Go (Gin) | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Yjs, payments:Razorpay, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R8-07 [P3_small_team] status=ok style=modular_monolith cost=$46-434
- stack: fr=Next.js | ba=Go (Gin) | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Yjs, payments:Stripe, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build
- warnings: ['BUDGET_UPPER_BAND:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R8-08 [P4_azure] status=ok style=modular_monolith cost=$428-3584
- stack: fr=React Native (Expo) | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure Container Apps
- supporting: auth:ASP.NET Core Identity, storage:Azure Blob Storage, payments:Razorpay, ml:Azure Machine Learning, cache:Azure Managed Redis, cdn:Azure Front Door, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['PHONE_OTP_CUSTOM:info']
- errors: []
- oracle violations: []

### R8-09 [P4_no_rbi] status=ok style=modular_monolith cost=$553-4271
- stack: fr=React Native (Expo) | ba=Spring Boot | da=Amazon RDS for PostgreSQL | ho=AWS ECS on Fargate
- supporting: auth:Amazon Cognito, storage:Amazon S3, payments:Stripe, ml:Amazon SageMaker, cache:Amazon ElastiCache, cdn:Amazon CloudFront, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R8-10 [P4_cheap] status=ok_with_warnings style=serverless cost=$405-2367
- stack: fr=React Native (Expo) | ba=NestJS | da=Amazon Aurora PostgreSQL | ho=AWS Lambda
- supporting: auth:Amazon Cognito, storage:Amazon S3, payments:Razorpay, ml:ONNX Runtime, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['BUDGET_EXCEEDED:warning', 'OPTIONAL_COMPONENT_DEFERRED:info', 'OPTIONAL_COMPONENT_DEFERRED:info']
- errors: []
- oracle violations: []

### R8-11 [P5_gcp_pref] status=ok_with_warnings style=monolith cost=$11-94
- stack: fr=Blazor | ba=ASP.NET Core | da=Google Cloud SQL for PostgreSQL | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['EOL_EXISTING_SYSTEM:warning']
- errors: []
- oracle violations: []

### R8-12 [P5_onprem] status=ok style=monolith cost=$0-121
- stack: fr=Blazor | ba=ASP.NET Core | da=Microsoft SQL Server | ho=Docker Compose on a Linux VM
- supporting: auth:Keycloak, storage:SeaweedFS, ci_cd:GitLab CI/CD (self-managed), observability:Sentry (self-hosted)
- warnings: []
- errors: []
- oracle violations: []

### R8-13 [P6_online_only] status=ok style=monolith cost=$1-74
- stack: fr=React Native (Expo) | ba=Django | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R8-14 [P6_ios_added] status=ok style=monolith cost=$1-74
- stack: fr=React Native (Expo) | ba=Django | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R8-15 [P6_strict] status=ok_with_warnings style=monolith cost=$1-74
- stack: fr=React Native (Expo) | ba=NestJS | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: ['SYNC_CONSISTENCY:warning']
- errors: []
- oracle violations: []
