p = 'tools/kb_source.py'
g = open(p, encoding='utf-8').read()

# hosting: managed Kubernetes on each hyperscaler (only for teams with DevOps, enforced by the engine)
anchor = 'add(H, "Docker Compose on a Linux VM"'
new_hosting = '''add(H, "Amazon EKS", cloud="aws", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(2, 3, 5, 5, 4, 5), ops=5, tags=("container", "kubernetes", "managed"), cap=500_000_000,
    cost=((90, 500), (6, 40)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed Kubernetes control plane for very large, multi-service workloads", "Runs in Mumbai and Hyderabad; full AWS ecosystem"),
    limits=("Needs real platform-engineering skills", "Control-plane fee plus node costs; slow to set up"),
    src=[("https://aws.amazon.com/eks/", "Amazon EKS")])
add(H, "Google Kubernetes Engine (GKE)", cloud="gcp", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(2, 3, 5, 5, 4, 5), ops=5, tags=("container", "kubernetes", "managed"), cap=500_000_000,
    cost=((75, 450), (6, 40)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Mature managed Kubernetes with autopilot mode", "Clusters in Mumbai (asia-south1) and Delhi (asia-south2)"),
    limits=("Needs real platform-engineering skills", "Overkill below a handful of services"),
    src=[("https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview", "GKE overview")])
add(H, "Azure Kubernetes Service (AKS)", cloud="azure", regions=ALLR, saas=True, htype="container", runtimes=("any", "docker"), ws=True, r=(2, 3, 5, 5, 4, 5), ops=5, tags=("container", "kubernetes", "managed"), cap=500_000_000,
    cost=((70, 450), (6, 40)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Managed Kubernetes integrated with Entra ID and Azure networking", "Indian Azure regions available"),
    limits=("Needs real platform-engineering skills", "Overkill for small teams"),
    src=[("https://learn.microsoft.com/en-us/azure/aks/what-is-aks", "What is AKS")])
'''
assert anchor in g
g = g.replace(anchor, new_hosting + anchor, 1)

# database: globally distributed SQL
anchor = 'add(D, "Supabase Postgres"'
new_db = '''add(D, "Google Cloud Spanner", langs=("sql", "java", "go", "python", "typescript"), cloud="gcp", regions=ALLR, saas=True, r=(3, 1, 5, 5, 4, 5), ops=1, tags=("relational", "managed", "multitenant", "global"), cap=2_000_000_000,
    cost=((65, 900), (8, 60)), comp=("pci_dss", "hipaa", "soc2", "iso27001", "gdpr"),
    strengths=("Horizontally scalable relational database with strong consistency, including multi-region configurations", "Instance configurations in Mumbai (asia-south1) and Delhi (asia-south2)"),
    limits=("Highest cost floor of the managed SQL options", "Google-specific dialect and features; GCP lock-in"),
    src=[("https://cloud.google.com/spanner/docs/overview", "Cloud Spanner overview"), ("https://cloud.google.com/spanner/docs/instance-configurations", "Spanner instance configurations")])
'''
assert anchor in g
g = g.replace(anchor, new_db + anchor, 1)

# frontend: .NET MAUI
anchor = 'add(F, "Flutter"'
new_fe = '''add(F, ".NET MAUI", langs=("csharp",), plat=("android", "ios", "desktop"), r=(4, 4, 4, 4, 4, 4), ops=1, tags=("mobile_cross", "offline_ok", "dotnet", "enterprise"), cap=20_000_000,
    strengths=("One C# and XAML codebase for Android, iOS, macOS and Windows", "Reuses .NET skills and libraries; natural pairing with ASP.NET Core"),
    limits=("No web target (pair with Blazor)", "Smaller community than Flutter or React Native"),
    src=[("https://learn.microsoft.com/en-us/dotnet/maui/what-is-maui", "What is .NET MAUI")])
'''
assert anchor in g
g = g.replace(anchor, new_fe + anchor, 1)
g = g.replace('"AWS EC2": (8, 60)', '"AWS EC2": (8, 60)', 1)
open(p, 'w', encoding='utf-8').write(g)

import json
rp = 'data/region_notes.json'
r = json.load(open(rp, encoding='utf-8'))
r["Amazon EKS"] = {"india": "AWS Mumbai (ap-south-1) or Hyderabad (ap-south-2)", "eu": "an EU region such as Frankfurt (eu-central-1)", "us": "a US region such as us-east-1"}
r["Google Kubernetes Engine (GKE)"] = {"india": "Google Cloud Mumbai (asia-south1) or Delhi (asia-south2)", "eu": "an EU Google Cloud region such as europe-west1", "us": "a US Google Cloud region such as us-central1"}
r["Azure Kubernetes Service (AKS)"] = {"india": "Azure Central India (Pune) or another Indian Azure region", "eu": "an EU Azure region such as West Europe", "us": "a US Azure region such as East US"}
r["Google Cloud Spanner"] = {"india": "Spanner instance configuration in Mumbai (asia-south1) or Delhi (asia-south2)", "eu": "an EU Spanner configuration such as europe-west1", "us": "a US Spanner configuration such as us-central1"}
json.dump(r, open(rp, 'w', encoding='utf-8'), indent=2)

a = open('tools/gen_kb_audit.py', encoding='utf-8').read()
open('tools/gen_kb_audit.py', 'w', encoding='utf-8').write(a)
print('kb patched')
