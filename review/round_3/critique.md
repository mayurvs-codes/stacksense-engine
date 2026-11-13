# Round 3 critique (statistical scan of 600 fuzzed scenarios + spot checks)

Instead of hand-writing scenarios, 600 new fuzzed scenarios (seed 31337, not used by the gate) were run through the engine and scanned by the
independent oracle plus extra heuristics for known-bad patterns: static generators for dynamic apps, non-relational databases without a need,
SQLite on non-persistent hosts, microservices, .NET-only auth libraries without a .NET backend, CDN for Android-only apps, "ok" status with cost far
above budget, static hosts with backends.

Result: 0 oracle violations, 0 hits for every heuristic except two:
- **Non-relational database without a need** (13 of about 550 viable stacks, e.g. Firestore for an API platform): scores were within 0.1-0.7 of the
  relational runner-up. Fix: stronger default penalty for document/key-value stores when there is no offline, gaming/social/IoT or write-heavy need.
  After the fix Firestore drops to the offline/mobile cases it suits (53 of 600 including offline and social scenarios).
- **Microservices**: 5 of 600 (0.8%), only with team >= 15, DevOps and the highest load tier: judged acceptable.

Round 3 therefore found one minor tuning defect (fixed); it is not counted as a clean round. A fourth clean round is still required by the
exit condition in `CLAUDE.md`.
