import re
r=open('README.md',encoding='utf-8').read()
r=r.replace('121 curated technologies','123 curated technologies')
open('README.md','w',encoding='utf-8').write(r)
n=open('docs/REPORT_NOTES.md',encoding='utf-8').read()
n=n.replace('curated 121-entry knowledge base','curated 123-entry knowledge base').replace('121 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 60 supporting.','123 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 62 supporting.').replace('The knowledge base has 121 entries','The knowledge base has 123 entries')
a=n.index('- P1 portfolio:'); b=n.index('(Explain in the report why each component')
new='''- P1 portfolio: Eleventy on GitHub Pages, no backend or database, estimated cost $0.
- P2 marketplace India: React Native (Expo) client for web+Android, NestJS on Google Cloud Run, Supabase Postgres in Mumbai, Razorpay, Firebase Authentication (phone OTP), Socket.IO, with an SEO limitation warning for the client-rendered web app.
- P3 whiteboard SaaS: Next.js, Go (Gin) on Google Cloud Run, Cloud SQL for PostgreSQL, Yjs for CRDT collaboration, Memorystore, Pub/Sub, Stripe.
- P4 lending India: React Native (Expo), Spring Boot on AWS ECS Fargate, Amazon RDS for PostgreSQL (Mumbai), Cognito, SageMaker, Razorpay, CloudFront, CloudWatch, with PCI DSS/RBI/DPDP/ISO 27001 notes.
- P5 internal HR tool: Blazor and ASP.NET Core on Azure App Service, reusing the on-premises SQL Server 2019 and Microsoft Entra ID, Azure Blob Storage.
- P6 offline crop survey: React Native (Expo) client, offline-capable Firestore (Mumbai) with a Django API on Google Cloud Run, Firebase phone OTP.
'''
n=n[:a]+new+n[b:]
open('docs/REPORT_NOTES.md','w',encoding='utf-8').write(n)
print('docs updated')
