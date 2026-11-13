"""Knowledge-base loader (data/kb/*.json) plus verified region notes and lifecycle rules."""
import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CORE = ("frontend", "backend", "database", "hosting")

# Names that betray a cloud vendor; used to cross-check the `cloud` tag of every KB entry.
CLOUD_PATTERNS = {
    "aws": re.compile(r"\b(aws|amazon|ec2|ecs|eks|fargate|lambda|elastic beanstalk|lightsail|app runner|amplify|dynamodb|aurora|rds|cognito|s3|cloudfront|sqs|sns|elasticache|opensearch service)\b", re.I),
    "azure": re.compile(r"\b(azure|app service|container apps|aks|cosmos db|azure sql)\b", re.I),
    "gcp": re.compile(r"\b(gcp|google cloud|cloud run|gke|cloud sql|firestore|bigquery|app engine|compute engine|cloud functions|spanner|alloydb)\b", re.I),
}

# End-of-life / retired technologies. Never recommended; reported when found in existing_systems.
LIFECYCLE_RULES = [
    (r"angularjs|angular\.js", "AngularJS reached end of life in December 2021"),
    (r"python ?2(\.\d+)?\b", "Python 2 reached end of life in January 2020"),
    (r"python 3\.[0-8]\b", "this Python 3 minor version is end of life"),
    (r"node(\.js)? ?(0|1[0-8]|[2-9])\b", "this Node.js major version is end of life"),
    (r"\.net (core )?(1|2|3\.1|5|6|7)\b", "this .NET version is out of support"),
    (r"sql server 20(05|08|12|14|16)\b", "this SQL Server version is out of Microsoft extended support"),
    (r"windows server 20(03|08|12)\b", "this Windows Server version is out of support"),
    (r"centos (7|8)\b", "CentOS Linux 7/8 are end of life"),
    (r"php ?[4-7]\b", "this PHP major version is end of life"),
    (r"xamarin", "Xamarin support ended in May 2024"),
    (r"parse\.com", "Parse.com was shut down in 2017"),
    (r"heroku free", "Heroku free dynos were discontinued in 2022"),
    (r"gatsby cloud", "Gatsby Cloud was wound down"),
    (r"iot core", "Google Cloud IoT Core was retired in 2023"),
    (r"dynamic links", "Firebase Dynamic Links was shut down in 2025"),
    (r"atlas device sync|realm sync|mongodb realm", "MongoDB Atlas Device Sync / Realm was deprecated"),
    (r"qldb", "Amazon QLDB reached end of support"),
    (r"codecommit", "AWS CodeCommit is closed to new customers"),
    (r"cloud source repositories", "Google Cloud Source Repositories is closed to new customers"),
    (r"\bmesos\b", "Apache Mesos was retired"),
    (r"\bsilverlight\b|\bflash\b", "browser plug-in technology is end of life"),
    (r"\bcoreos\b|\bbower\b", "this project is retired"),
]


def lifecycle_issue(text):
    low = str(text).lower()
    for pat, why in LIFECYCLE_RULES:
        if re.search(pat, low):
            return why
    return None


class KB:
    def __init__(self):
        self.layers = {}
        for f in sorted((DATA / "kb").glob("*.json")):
            for e in json.loads(f.read_text(encoding="utf-8")):
                self.layers.setdefault(e["layer"], []).append(e)
        for layer in self.layers:
            self.layers[layer].sort(key=lambda e: e["name"])
        self.region_notes = json.loads((DATA / "region_notes.json").read_text(encoding="utf-8"))

    def layer(self, name):
        return self.layers.get(name, [])

    def get(self, layer, name):
        for e in self.layers.get(layer, []):
            if e["name"] == name:
                return e
        return None

    def region_note(self, name, residency):
        return self.region_notes.get(name, {}).get(residency)


@lru_cache(maxsize=1)
def load():
    return KB()
