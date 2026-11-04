# 0051: Two stale atlas pages brought up to date: the corpus profiled again (U0), and the audit's findings followed forward

**Date:** 2026-11-04. **Whose:** the owner asked for U0's page and the audit page, and any others out of date, to be
updated; Claude chose how.

**Context.** Two pages of the evidence atlas no longer described the project as it stands.

1. **U0** (the corpus at a glance) quoted the corpus profile of 25 October 2026: 162 tables from 41 sources. The
   corpus has 54 sources (the data page and the source register said so), because 13 were added after that profile
   (`ror`, IP Australia's register and API harvests, the provisionals, and the data gaps filled after Stage 2), with
   29 tables; three tables were added to existing sources and eight rebuilt. The profile had not been re-run, so the
   notebook's U0 matched its own output, and the page matched the notebook, but both described a corpus that no
   longer existed. The chart's source line in the notebook also gave the first profile's date (22 October). The
   corpus lens page said 41 sources in one place and 42 in another, as did the glossary.
2. **The audit page** (`#/audit`, ADR 0025) showed the review against IP Australia as made on 27 October 2026. The
   same day, the register check (ADR 0027, 0028) and its fills (ADR 0029) settled one of its four disagreements (D1,
   designs of unknown origin), showed IP RAPID was not the odd one out on another (D2, 2018's trade marks), and
   reworded its three questions to IP Australia; Stage 3 later tested three of IP Australia's conclusions (M5, M25,
   M35). The page still said the cause of D2 was unknown, that design shares were lower bounds, that "the observation
   pages ... are unchanged", and gave the questions' first wording.

**Decision.**

1. **The corpus is profiled again** (`analysis/profile_corpus.py`, all stages): 194 tables from 54 sources, 335,184,272
   rows, every table opening and matching the manifest. `tables.csv`, `columns.csv`, `keys.csv` and `PROFILE.md` are
   regenerated.
2. **Notebook 1: U0's two code cells are re-run alone** (with the setup cell; never the notebook in full, as
   `CLAUDE.md` requires), and U0 quotes the new output with a dated correction that keeps the earlier figures. The
   chart's source line gives the new date. No other cell changes. `docs/stage-1-summary.md` follows, with a dated note.
3. **The atlas follows**: U0's page, its chart (checks updated to the new figures, redrawn alone), the corpus lens,
   the data page's introduction, the glossary, and an entry in the corrections log.
4. **The audit's record is not rewritten; it gains a dated section** (`docs/audit-ip-australia.md`, section 10, "Since
   the audit"), quoting each later figure from the record that holds it (`docs/audit-ipa-api.md`,
   `docs/recheck-oq6-oq7-oq13.md`, the notebooks). The verdicts in section 5 stay as given on 27 October, against the
   observations as they then read. The benchmark, re-run against the lenses rebuilt today, is unchanged (195 figures,
   155 agreements), and section 10 says so.
5. **The audit page says where each finding now stands**: a banner saying what the page is and when; a "Since the
   review" section after "In brief" (settled, narrowed, still open, done, not covered); a "Since then" note on each of
   the four disagreements; the later tests of C1, C3, C5 and C8; the questions in their current wording; the changes
   list with each one's status; and a limit saying the review covers U0 to U98 only. D2's heading no longer says IP
   RAPID is short. The numbers rule holds: every figure is in the record or the benchmark's outputs.

**Rejected.** Re-running the audit to cover U99 to U127 and Stages 2 and 3: that is a new review, for the owner to
ask for. Changing the audit's verdicts in place: they are a dated record of what the review found.

**Consequences.** `uv run python analysis/profile_corpus.py` should be run whenever a source is added, as U0's page
says; the next run will move U0 again. The audit page is now accurate as at 4 November 2026; a reply from IP
Australia to OQ12 to OQ14 would change its "Since the review" section.
