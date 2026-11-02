# 0037: Origin is the filer's, from one party, everywhere a claim is about who files

**Date:** 2026-11-02. **Whose:** the owner asked for pass 2 of the external notebook audits, the origin fix (A18,
OQ23); Claude decided how. The findings acted on, and the check of each, are in
`analysis/GPT-audit/261030/AMENDMENTS.md`.

**Context.** ADR 0013 set the rule that "where and who files" uses the founding applicants and "who holds" the current
ones, and ADR 0024 found that a founding applicant in Australia (`founding_australian`) reproduces IP Australia's own
count of resident applications. The `regions` and `firms` lenses switched (ADR 0016, 0017); the rest did not:
1. **Holder for filer.** The `timeline` lens's Australian, overseas and unknown series (`ORIGINS` in `build.py`) and
   the `industries` lens's `patents_standard_au`, `patents_standard_au_with_services` and `trade_marks_au` counted by
   the current holder (`australian_applicant`), and so did notebook 1's origin, type, place, route and family
   observations (U7, U8, U13, U15, U67, U90 to U94, U99 to U102, U115) and notebook 2's B55.
2. **Two parties for one filer.** `founding_australian` is true if any founding applicant is in Australia, but
   `founder_type` is the first founding applicant's, whatever its country. Stage 2's filer groups (`FILER`, B5 to B19)
   and several notebook 1 cells paired them, and the `regions` lens counted organisations' filings at the first
   Australian founder's postcode by the first founder's type.
3. **Unknown read as overseas.** `FILER` sent an unknown origin to "overseas" wherever a query did not filter it out
   (B12).

Checked before acting: holder and filer origin disagree for 0.2% to 1.8% of rights in each type and period, moving
yearly Australian shares by up to 0.7 points for standard patents, 1.6 for designs and 4.4 for plant breeder's
rights; the second party's type differs for at most 0.121% of Australian-founded rights; B12's slip reaches at most
224 patents. Small, but against the project's own rule, and the timeline and industries lenses are inputs to Stage 3.
Against the World Bank's resident patent count (WIPO's), 1989 to 2024, the median ratio is 1.0017 by the holder,
1.0110 by any founding applicant and 1.0006 by the first: WIPO counts a resident by the first-named applicant.

**Decision.**
1. **Filer's origin for filer claims.** `timeline` and `industries` count Australian and overseas applications by
   `founding_australian`, IP Australia's definition. Every notebook query that says who filed or from where uses it.
   `australian_applicant` stays for who holds a right (B19 and B26, rights moving overseas).
2. **`rights.filer_group`:** origin and type of one party: `australian_` and the type of the first founding
   applicant in Australia if any founder is Australian; else `overseas_` and the type of the first with a known
   country; empty if no founding applicant has a country. Stage 2's `FILER` is made from it, so an unknown origin is
   never "overseas".
3. **`rights.founding_australian_filled`:** the filer's origin, filled from the register's owner only while the right
   has not changed hands, as `filer_abn` is (ADR 0029); U102's filled design shares use it. `australian_applicant_filled`
   stays as the holder's.
4. **`regions`** counts organisations' filings by the same party that gives the postcode
   (`filer_group = 'australian_organisation'`).
5. **WIPO comparisons** (U67) show the first founding applicant's country beside IP Australia's definition.

**Rejected.**
- **The first founding applicant's country as the lens's origin.** It is nearer WIPO's count, but IP Australia's
  definition (any founding applicant) is the one the research reports against, reproduces IP Australia's resident
  counts exactly (ADR 0024), and IP RAPID gives no order of applicants on the application: "first" is by the date the
  party was recorded, then party id.
- **The register's fill in the timeline's series.** Fills sit beside IP RAPID's values, never in place of them (ADR
  0029); the timeline's design series keep IP RAPID's unknown share, and U102 gives the filled shares.
- **Changing `founder_type` itself.** Its meaning (the first founding applicant's type) is used by `institution_rights`
  and the firms lens's checks; `filer_group` carries the paired meaning instead.

**Checked.**
- `tests/test_eda.py::test_filer_origin_comes_from_one_party_and_feeds_the_timeline`: `filer_group` is empty exactly
  where the filer's origin is unknown (or that party has no type) and its prefix is `founding_australian`; the filled
  origin never changes a known one; the timeline's standard patent series equal the rights counted by the filer's
  origin, month by month.
- `rights` 4,356,908 rows and 88 columns (two added); `timeline`, `industries` and `regions` unchanged in shape.
  `python -m audit.benchmark` is unchanged: it already used `founding_australian` (ADR 0024).
- Both notebooks re-executed; every observation quoting a moved figure restated (`AMENDMENTS.md` lists them), each
  with the earlier figure where a reader might have used it. Conclusions that changed: trade marks' FY1995 share is
  no longer given (the founding applicant's country is missing for 6.3%); the Designs Act 2003's rush from overseas
  is within the placebo range (12.5%), its step still beyond it (B47); the October 2016 trade mark cut's step from
  overseas is at the threshold (5.556%), so fee changes show 3 rushes and 2 steps beyond 95% of placebos, not 4 and 3.
- Not changed here: the evidence atlas (its own pass); `tests/test_atlas.py` stops at its numbers rule until then.
