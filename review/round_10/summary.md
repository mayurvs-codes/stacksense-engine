# Round 10 engine outputs (auto-generated)

10 scenarios, 0 with oracle violations

### R10-01 [k8s_justified] status=ok style=microservices cost=$6678-40375
- stack: fr=Next.js | ba=Go (Gin) | da=Google Cloud Spanner | ho=Google Cloud Run
- supporting: auth:Microsoft Entra ID, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R10-02 [global_sql] status=ok style=microservices cost=$44078-272673
- stack: fr=Next.js | ba=Spring Boot | da=Google Cloud Spanner | ho=Google Cloud Run
- supporting: auth:Keycloak, payments:Stripe, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R10-03 [maui_pos] status=ok_with_warnings style=modular_monolith cost=$19-114
- stack: fr=.NET MAUI | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Microsoft Entra ID, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: ['OFFLINE_SYNC_CUSTOM:warning']
- errors: []
- oracle violations: []

### R10-04 [small_no_k8s] status=ok style=modular_monolith cost=$42-269
- stack: fr=HTMX with server-rendered templates | ba=Go (Gin) | da=Azure SQL Database | ho=Azure App Service
- supporting: auth:Firebase Authentication, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R10-05 [azure_k8s_big] status=ok style=service_oriented cost=$3531-22862
- stack: fr=None | ba=ASP.NET Core | da=Azure SQL Database | ho=Azure App Service
- supporting: cache:Azure Managed Redis, queue:Azure Service Bus, ci_cd:Azure DevOps Pipelines, observability:Azure Monitor
- warnings: []
- errors: []
- oracle violations: []

### R10-06 [eu_k8s_gdpr] status=ok style=service_oriented cost=$3418-18521
- stack: fr=Next.js | ba=Spring Boot | da=Amazon RDS for PostgreSQL | ho=Amazon EKS
- supporting: auth:Amazon Cognito, cache:Amazon ElastiCache, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: []
- errors: []
- oracle violations: []

### R10-07 [student_proj] status=ok_with_warnings style=monolith cost=$0-36
- stack: fr=HTMX with server-rendered templates | ba=Django | da=Supabase Postgres | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, ci_cd:Google Cloud Build
- warnings: ['BUDGET_EXCEEDED:warning', 'LAUNCH_ABOVE_TWELVE_MONTHS:info', 'OPTIONAL_COMPONENT_DEFERRED:info', 'PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R10-08 [iot_cloud] status=ok style=service_oriented cost=$55-241
- stack: fr=None | ba=Go (Gin) | da=Amazon DynamoDB | ho=AWS ECS on Fargate
- supporting: cache:Amazon ElastiCache, queue:Amazon SQS, ci_cd:AWS CodePipeline, observability:Amazon CloudWatch
- warnings: ['PEAK_ABOVE_USERS:info']
- errors: []
- oracle violations: []

### R10-09 [india_social_k8s] status=ok style=service_oriented cost=$4963-45860
- stack: fr=React Native (Expo) | ba=Spring Boot | da=Firestore | ho=Google Cloud Run
- supporting: auth:Firebase Authentication, storage:Google Cloud Storage, realtime:Centrifugo, cache:Google Cloud Memorystore, queue:Google Cloud Pub/Sub, cdn:Google Cloud CDN, ci_cd:Google Cloud Build, observability:Google Cloud Operations Suite
- warnings: []
- errors: []
- oracle violations: []

### R10-10 [gov_onprem_k3s] status=ok style=modular_monolith cost=$170-1742
- stack: fr=HTMX with server-rendered templates | ba=Spring Boot | da=PostgreSQL | ho=Kubernetes (k3s) on-prem
- supporting: auth:Keycloak, search:Meilisearch, cache:Redis (self-hosted), queue:RabbitMQ, ci_cd:GitLab CI/CD (self-managed), observability:Grafana + Prometheus
- warnings: []
- errors: []
- oracle violations: []
