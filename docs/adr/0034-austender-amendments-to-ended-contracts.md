# 0034: AusTender amendments published after August 2019 to contracts that had ended by then

**Date:** 2026-10-29. **Whose:** the owner asked for the data gaps to be filled (A15, `docs/data-gaps-brief.md`, gap
B10; OQ3); Claude measured the gap and chose the fix.

**Context.** `austender` combines the Department of Finance's bulk file (notices published to 30 August 2019) with the
OCDS API: notices by the date published from July 2019, and every release of each contract still running on 30 August
2019, asked by id. Amendments published later to contracts that had *ended* by then are in neither part. OQ3 took
them to be under 1% of value. A contract's value in the lenses is its latest notice's, so a missing amendment leaves
the contract at an old value.

**What a sample showed** (`analysis/audit/austender_amendments.py`; 500 contracts in each band of end dates, the
lowest hash of their id; amendments counted only when numbered beyond the bulk file's last, since the API also
re-released old notices with new dates):

| Contracts that ended | Contracts | With amendments the corpus lacks | Amendments |
|---|---|---|---|
| September 2018 to August 2019 | 53,888 | 38 of 500 (7.6%) | 65 |
| September 2017 to August 2018 | 57,908 | 36 (7.2%) | 65 |
| September 2015 to August 2017 | 116,782 | 27 (5.4%) | 37 |
| before September 2015 | 552,031 | 8 (1.6%) | 10 |

The value they add is heavy-tailed: one contract in the most recent band rose by $88 million (from $1.55 billion), so
a sample cannot size it (scaled up, from 0.14% to 29.8% of a band's value). Most of the late amendments carry the
API's batch release date (27 April 2023), so their true dates are unknown.

**Decision.**

1. **Ask by id for every contract that ended in the four years before 30 August 2019** (from 1 September 2015:
   234,313 contracts, about nine hours at 7 to 8 a second). They hold nearly all the late amendments (5% to 8% of
   them have one, against 1.6% of the older ones), and every contract the `regions` lens counts (first published in
   FY2017 or later) that had ended by then. Older contracts' late amendments are left out, as the source's docstring
   says; they reach the `firms` and `institutions` lenses, which count contracts of every year.
2. The answers are a third raw file (`austender-api-by-id-ended-releases.jsonl.gz`, R2), read like the other by-id
   file: a notice the API holds replaces the bulk file's, so each contract's latest notice is its latest anywhere.
3. The lenses that use AusTender (`firms`, `regions`, `institutions`) are rebuilt, and the observations quoting their
   contract counts or values are checked against the re-run notebooks.

**Consequences.** Recorded in the handover once the harvest and the re-run are done.
