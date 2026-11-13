p='tools/write_progress.py'
s=open(p,encoding='utf-8').read()
s=s.replace('110 unit and property tests','116 unit and property tests').replace('110 pass','116 pass')
s=s.replace('''- 110 unit''','''- 116 unit''')
s=s.replace('''## Round 2: adversarial review (`review/round_1`, `review/round_2`, `review/round_3`)''','''## Rounds 2-5: adversarial review (`review/round_1` ... `review/round_5`)''')
s=s.replace('''- 32 + 25 hand-designed scenarios and a 600-scenario fuzz scan, each output read critically (critique files in each folder).''','''- 32 + 25 + 25 hand-designed scenarios and 8 fuzz scans of 600 scenarios each (`tools/scan.py`), outputs read critically (critique file in each folder).
- Round 4 additionally fixed: a scoring bug that rewarded stacks for merely having more components (a 30M-user static site landed on Cloud Run),
  backends on static hosts, EOL databases (MongoDB) abandoned instead of upgraded, unattested SaaS under HIPAA/PCI, RBI + residency conflicts.''')
s=s.replace('''- Exit condition (b) is NOT formally met: round 2 found defects and round 3 found one minor tuning issue, so there has not yet been a clean
  round, let alone two in a row. More adversarial rounds are recommended.''','''- Exit condition (b): the last hand-written round (4) still found defects, which were fixed. After the last fix, 7 further fuzz scans (4,200 scenarios)
  found 0 oracle violations and only a borderline heuristic hit (about 1% Firestore-for-realtime/GCP choices, judged defensible). A fresh hand-written round
  after the last fix has NOT been done, so the "two consecutive clean rounds" condition is not formally proven.''')
open(p,'w',encoding='utf-8').write(s)
