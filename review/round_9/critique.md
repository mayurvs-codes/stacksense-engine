# Round 9 critique (robustness fuzz + explanation-text review)

Different angle from earlier rounds: instead of new architectures, attack the engine's behaviour at the edges and read the generated prose as a judge.

**Robustness (`tools/garbage_fuzz.py`, 6,000 mutated scenarios, wrong types, NaN, huge ints, unicode, deleted fields, bad `extra`):** 0 crashes, every result valid
JSON with a legal status; invalid inputs always carry field errors. Web API: empty body, malformed JSON, list body, invalid UTF-8 all return `invalid_input` with
HTTP 200 JSON; unknown paths return 404. Extreme but valid values: 10^30 users produced a cost band of about 10^27 USD (silly, not a crash).

**Prose review (P4 output read end to end):**
| # | Defect | Fix |
|---|---|---|
| 1 | absurd scale (10^30 users) produced astronomically large cost bands | scale clamped to 10 billion for estimation, with an assumption stating it |
| 2 | storage justification repeated the data-residency sentence twice | generic residency clause skipped for storage (it already states the region) |
| 3 | hosting counterfactual for AWS ECS on Fargate said "move to a container or serverless platform on a hyperscaler" (circular) | counterfactual tailored: large-cap hosts suggest multi-region, service split and sharded/global datastore; small-cap hosts suggest moving to a hyperscaler |
| 4 | clumsy wording "A team.experience=senior team of team.size=8" | rewritten: "For a senior team of 8 engineers (team.experience=senior, team.size=8) ..." |

Remaining prose limitation: `why_not` texts name only the weighted criterion with the largest deficit, so a runner-up that is better on other criteria (for
example Aurora on scalability) is described by its weakest dimension only.
