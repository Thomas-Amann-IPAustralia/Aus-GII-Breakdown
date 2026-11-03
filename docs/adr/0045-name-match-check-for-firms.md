# 0045: Stage 3 checks firms' IP counts with a name match to the ABR

**Date:** 2026-11-03. **Whose:** the owner's (A30: add the check to the Stage 3 plan); how it is done is Claude's, and
the owner can overturn any of it.

**Context.** Firms' IP counts are lower bounds (U41): a right is credited to a firm only where IP RAPID, or IP
Australia's register (ADR 0029), gives the filer's ABN. Applicants are identified by name and address; an ABN is
attached only where one is given or matched. With the register's ABNs, 90.9% of Australian organisations' trade marks
filed in FY2026 carry one, but standard patents fall from 88.7% (FY2024) to 83.9% (FY2026) and cannot be filled from
the register (U45, U100, U101). The corpus holds every ABN (the ABR's bulk extract, 20,612,369 rows, with the main
name of every non-individual) and ASIC's company names, so the unlinked rights could be matched by name, at no cost.

**Decision.** In Stage 3, before the firm findings are read as settled:
1. **Who is matched:** rights whose filer is an Australian organisation (by `founder_type` and the filer's country) with
   no filer's ABN from either source. Individuals are out of scope: the ABR's public extract keeps no sole traders'
   names, and the corpus does not hold personal names for linking.
2. **How:** names normalised (case, punctuation, "Pty Ltd" and other legal endings, "The"), then matched to the ABR's
   main names and ASIC's company names; a match is kept only if it is unique, and the state (and the postcode, where
   both are known) agrees. Trading names and fuzzy matches are reported apart, not used, unless the test below shows
   they are reliable.
3. **Tested first:** on rights that do have an ABN, the ABN is hidden and the match is run; the share recovered, and the
   share matched to the wrong ABN, are reported by right type and period. The match is used only if its error rate is
   stated beside every result that uses it.
4. **Kept apart:** the matched links go in their own columns of the `firms` lens (for example `n_trade_marks_name_matched`),
   described in `analysis/eda/variables.yaml`, and are never added to the `n_*` counts (one row per key, no two sources
   added for one measure, ADR 0007).
5. **Used as a check:** U44, U45 and the Stage 2 leads that use firm counts are rerun with the matched links; each
   result says whether it changes. Adopting the matched links into the counts is the owner's decision.

**Rejected.**
- **Adding matched links to the counts now:** it would mix an exact link with an estimated one, before its error is known.
- **Waiting for IP Australia (OQ7):** the request explains IP RAPID's gap; it does not supply the missing patents'
  ABNs, and the check costs nothing.
- **Fuzzy matching by default:** common and similar names (groups of related companies, trustees) would add wrong links
  that cannot be told from right ones without the test.
