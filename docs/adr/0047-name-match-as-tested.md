# 0047: The name match as tested: the filer's name and state, unique, kept in its own columns

**Date:** 2026-11-03. **Whose:** Claude's, carrying out ADR 0045 (the owner's A30); the owner can overturn any of it.
Adopting the matched links into the counts stays the owner's decision (ADR 0045, point 5).

**Context.** ADR 0045 set the check: Australian organisations' rights with no filer's ABN are matched by name to the
ABR's main names and ASIC's company names, a match kept only if it is unique and "the state (and the postcode, where
both are known) agrees", tested first on rights whose ABN is known. The corpus's ABR extract holds each ABN's main name
(not its trading or business names); ASIC's register holds each company's current and former names. Since FY2000,
159,000 or so Australian organisations' rights have no filer's ABN (117,531 trade marks, 18,317 provisionals, 9,104
standard patents, 8,275 designs), and every one has its filer's name in IP RAPID's parties.

**What the test found** (rights with a known ABN, the ABN hidden; by type of right and decade, FY2000 to FY2026):
- With the state and the postcode agreeing where both are known, 32% to 58% of rights are matched, and 1.2% to 4.8%
  of the matches name another ABN (designs filed FY2000 to FY2009, 15.0%).
- With the state alone, 64% to 83% are matched, and 1.1% to 4.8% of the matches name another ABN (those designs,
  9.8%). The postcode halves the matches without making them more accurate: IP RAPID records the filer's address as
  first recorded, the ABR its current one, and firms move.
- The rights that lack an ABN match far less often (8% to 35% with the state alone): their filers' names are less
  often an ABN's main name (a trading name, a company since renamed beyond ASIC's record, or one never registered).

**Decision.**
1. **The match uses the state, not the postcode**: the filer's name key (`build._name_key`: capitals, no punctuation,
   no "The" or legal endings) against the main names of every ABN that is not an individual's and every current and
   former ASIC company name (through its ABN, or its ACN where the ABR gives that ACN one ABN); kept only if exactly
   one ABN has the key and is registered in the filer's state.
2. **Kept apart**, as ADR 0045 requires: `name_matched_abn` in the `rights` lens (only where the filer is an Australian
   organisation and `filer_abn` is empty), and `n_patents_standard_name_matched`, `n_patents_provisional_name_matched`,
   `n_trade_marks_name_matched` and `n_designs_name_matched` in the `firms` lens, for ABNs the lens already holds. No
   row is added and no `n_*` count changes; a test checks both.
3. **Its error rate goes with every result that uses it**: the tested share of matches that name another ABN, by
   type and decade (`03_multivariate.ipynb`, section 2.5). A "wrong" ABN can be a related company of the same group
   (the test cannot tell), so the rate is an upper bound on error of that kind and a fair measure of the rest.

**Rejected.**
- **The postcode as well**, as ADR 0045 first set it: it halves the matches for no gain in accuracy.
- **Trading names and fuzzy matching:** the ABR extract in the corpus has no trading names, and fuzzy matching was
  left out by ADR 0045 unless the test showed exact matching to be reliable; it is reliable, and recall on the
  unlinked rights, not accuracy, is its limit.
- **New rows for matched ABNs the lens does not hold:** it would change the lens's population and every earlier
  figure that counts firms.

**Consequences.** The `rights` lens gains one column and the `firms` lens four; `variables.yaml` and `screens.yaml`
describe them (the name match is not screened). The build takes about a minute longer. U44, U45 and the firm leads
are rerun with the matched links in section 2.5, without changing notebooks 1 and 2 (the website is frozen, A32).
