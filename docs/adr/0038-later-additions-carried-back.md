# 0038: Later additions carried back: one current account, with the first wording dated

**Date:** 2026-11-02. **Whose:** the owner asked Claude to continue checking the external notebook audits and to
correct what holds (A19); Claude chose the theme (the sweep that passes 1 and 2 proposed) and how. The findings acted
on, and the check of each, are in `analysis/GPT-audit/261030/AMENDMENTS.md` (pass 3).

**Context.** Twenty-five audit findings, in all twelve audits, say the same thing: material added after an
observation was written (the data gaps filled after Stage 2, A15; the register's fills, ADR 0029; passes 1 and 2) was
appended later in the notebook without retiring what it superseded. Checked one by one against both notebooks, the
lenses as built and both stage summaries, 19 hold in full and 6 in part (none is false). The kinds:
1. **Subtotals labelled as totals.** Three attachment inventories leave out the sources added after Stage 2 in their
   queries but call the result the total: `region_indicators` 22,511,923 of 28,960,234 rows (U55), `national_indicators`
   41,218,170 of 41,230,072 (U68), `industry_indicators` 1,409,875 of 1,425,157 (U79); Stage 2's places screen (B28)
   is the five-source subset without saying so. The Stage 1 summary's lens table quoted all three.
2. **Leads and decisions left standing after they were settled.** U34's November 2018 "lead" and its one-side-only
   decision (settled by U103); U27's and U29's leads (settled by U38 and U39); U45's "a lead" and its chart of IP
   RAPID's ABNs alone (settled by U100 and U101); U49's "will count" (measured by U87); U75's and §6.7's "a services
   crosswalk is future work" (done in U114); U28's and §9's "fees still missing" (U108 to U111); B11's "the gap
   narrowed" and §1.9's "replicated" (B55); B61's "B34's gap holds" (B34 finds none in 2016 to 2020).
3. **Stale counts and pointers.** U0's lens table (rights 4,368,006 before the empty designs were dropped, firms
   398,450 before the register's ABNs, against 4,356,908 and 463,279 now), U22's columns (35, then 61; 79 now), U23's
   "fifteen" series (its table has 18), §9's section pointers, §3.7's B28 count (24,948, moved to 24,947 by pass 2), and
   the Stage 1 summary's firms section (398,450 ABNs, five schemes, a median age of 13.6).
4. **Qualifications dropped in summaries.** U53's range mixing postal areas and SA3s; B29's "1.7 to 1.9" (standard
   patents, unadjusted) and a joint model claimed for SA3s that was not fitted; "divisions near certain" for
   concentrated crosswalk weights; "named most often" with no tally; the caption saying designs' origin is "recorded for
   few Australian designs" (it is unknown for 4.0% to 25.1% a year).

**Decision.**
1. **One current account in each observation.** The heading and the decision say what is now known; the first wording
   follows in a dated "Restated (2 November 2026, audit ...)" line where a reader might have used it. This is the
   notebooks' existing convention (passes 1 and 2), used as the change log the audits ask for, rather than moving
   superseded text to a separate log.
2. **Inventories show the whole and the part.** Where an analysis rests on a subset chosen at the time (the five-source
   places screen, U68's profile), the subset stays, labelled, and the query prints the reconciliation to the current
   total. Re-running Stage 2's screen with the later sources would change its false discovery family, and the later
   sources were worked as planned pairs instead (B58, B59).
3. **Rows, not values; selected tables, not all a source publishes.** "Every value they publish" becomes "the values
   ingested from their selected tables"; an inventory counts rows, and says how many are empty or text.
4. **Not changed:** the register's fills stay beside IP RAPID's columns (ADR 0029, A12), though one audit asks for the
   filled results to be made primary; the observation explains both. Stage 2's screens are not re-run.
5. **A forward pointer for every gap filled later,** and a "proposed, not done" where a remedy was only proposed (U49,
   U87's institutional placement).

**Consequences.** Both notebooks and both stage summaries read as of 2 November 2026, with no new analysis except
three compact outputs that put an existing claim on the page: designs' origin caption, gross value added's profile
(U73) and the count of WGEA reporters under 100 employees (U112). No conclusion carried to Stage 3 reverses; three are
narrowed: B11 and B12 hold from FY2010 only, B61 is no longer evidence of under-patenting, and value added (37 years,
every division) reopens a longer industry comparison for Stage 3. The evidence atlas is not updated (the web pass is
the owner's call).
