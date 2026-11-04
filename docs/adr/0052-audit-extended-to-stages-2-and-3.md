# 0052: The audit against IP Australia extended to U99 to U127 and Stages 2 and 3

**Date:** 2026-11-04. **Whose:** the owner's (what: A35, to check Stage 1's later observations and Stages 2 and 3 as
the audit of 27 October checked U0 to U98, in a later session); Claude's (how, and every verdict), which the owner can
overturn. The full account is section 11 of [`docs/audit-ip-australia.md`](../audit-ip-australia.md); sections 1 to
10 are as they were.

**Context.** ADR 0024 audited Stage 1's 99 observations against IP Australia's published figures; ADR 0051 followed
its findings forward and recorded that the 130 observations since (U99 to U127, B1 to B63, M1 to M38) had not been
checked. Stages 2 and 3 read associations, which IP Australia rarely publishes, and its research on firms uses the
ABS's BLADE, which this project cannot (OQ9).

**Decision.**

1. **The same method** (ADR 0024): IP Australia's twelve IP Reports, its research papers and its analytical notes in
   the Econ repository's knowledge base, searched by the new observations' topics; IP Australia's definitions
   (calendar years, `founding_australian`); the same tolerance and verdict scale. A "consistent" verdict on a Stage 2
   or 3 observation says IP Australia's evidence points the same way, usually on other data or with another design,
   not that it confirms the size.
2. **13 figures added to the benchmark**, all agreeing: Australians' designs with the register's country (2014,
   2021, 2023, 2025; within 0.57%, U99, U102), the six fees the IP Report 2015 lists (exact, U108), and 2019's
   divisional applications (-2.92% against -2.9%, -0.54% against -1.2%, 86.21% of residents' fall against 87%; B15,
   M26). The benchmark holds 208 figures, 168 agreeing; the first 195 are unchanged. `benchmark.py` gains a fee (read
   on 1 March of the edition's year) and a change on the year before; `tests/test_audit.py` allows an observation of
   any notebook (U to 127, B to 63, M to 38) and checks the second pass's verdicts one per observation.
3. **Verdicts for the 130:** 3 corroborated (U99, U102, U108), 28 consistent, 6 qualified (B45, B56, B63, M5, M23,
   M36), none disputed or contradicted, 93 not testable. With ADR 0024's, all 229 observations have a verdict.
4. **Three measures corroborated for the first time:** the register's origin for designs, the fee lens's level, and
   the divisional flag.
5. **Four of IP Australia's conclusions added (C13 to C16):** trade marks lead real GDP (an analytical note); larger
   and older firms use IP, and R&D goes with patents (BLADE); research funding raises research organisations'
   patenting, collaborative grants more; the 1996 fall in trade mark filings reflects multi-class applications. None is
   adopted.
6. **The qualified six are caveats, not disputes.** B56, B63 and M36 compare changes in the same quarter, where IP
   Australia's note finds a lead; M5's expedited examination is narrower than the commissioned study's "speeding up",
   which includes early unprompted requests (41.9% of granted patents), and the study itself finds delay helps small
   innovators, as M5 does; B45 and M23 compare universities, where IP Australia followed each organisation over time.
7. **The atlas's audit page shows both passes** (`analysis/atlas/audit.py` reads the record's sections 11.3 and 11.4
   as it reads 5.1 and 5.2; a second verdict chart; a plain-English note for each of the 37 tested; C13 to C16; the
   "not covered" item and limit closed). The observation pages are not changed.
8. **The notebooks are not rewritten:** IP Australia's figures are not among their outputs.

**Consequences.** Every observation now stands beside IP Australia's published evidence, or is recorded as having
none. Three tests IP Australia's research suggests are put to the owner as OQ27 (direction): trade marks' lead on GDP,
early unprompted examination requests against years in force, and funding within institutions over time. Agreement
still shows the lenses read the register as IP Australia does, not that the register is right.
