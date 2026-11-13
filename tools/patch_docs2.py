for f in ('README.md','docs/REPORT_NOTES.md'):
    t=open(f,encoding='utf-8').read()
    t=t.replace('123 curated technologies','124 curated technologies').replace('123-entry','124-entry').replace('123 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 62 supporting','124 entries: 15 frontend, 11 backend, 16 database, 19 hosting, 63 supporting').replace('has 123 entries','has 124 entries')
    open(f,'w',encoding='utf-8').write(t)
w=open('tools/write_progress.py',encoding='utf-8').read()
w=w.replace('123 entries after round 2','124 entries after round 8').replace('120 unit and property tests','122 unit and property tests').replace('120 pass','122 pass').replace('- 120 unit','- 122 unit').replace('Rounds 2-7: adversarial review (`review/round_1` ... `review/round_7`)','Rounds 2-8: adversarial review (`review/round_1` ... `review/round_8`)')
w=w.replace('Defects per hand-written round: 12+, 6, 5, 1, 3, so','Round 8 (15 modified versions of the public scenarios, the kind the judges said they would run) found one (static host given a search server; fixed with Pagefind). Defects per hand-written round: 12+, 6, 5, 1, 3, 1, so')
open('tools/write_progress.py','w',encoding='utf-8').write(w)
