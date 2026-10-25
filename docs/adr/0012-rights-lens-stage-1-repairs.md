# 0012: Five repairs to the rights lens, found in its Stage 1 profile

**Date:** 2026-10-25. **Whose:** Claude's, while profiling the `rights` lens in Stage 1 (the owner asked for the
univariate section to begin); the owner can overturn any of it. It changes ADR 0009 and 0010's definitions of
`has_agent`, `main_area`, `registered_date`, `days_to_registration`, `retired_date` and `applicant_state`. The evidence
for each repair is in `analysis/notebooks/01_univariate.ipynb`, section 1.0 (and 1.7 for the state), read from IP
RAPID's own tables so that it stays on the page after the repair.

**Context.** ADR 0007 asks for a table's known errors to be repaired before its Stage 1 section. Profiling every column
of `rights` found five more: two placeholder dates, a measure that measured nothing for old trade marks, a column that
held a different classification for most rights, a flag that overstated attorney use, and a state left out of recent
records.

**Decision.**
1. **`has_agent` counts only an agent who is not the applicant.** IP RAPID's "agent" is the address for service, which
   is often the applicant's own. Its flag named an agent for 100% of trade marks and of Australian applicants' designs
   filed FY2017 to FY2026. `has_agent` is now true only if an agent on the record (at any time) is not one of the
   right's applicants or owners, by party id or by name with case and punctuation removed. For Australian applicants
   (FY2017 to FY2026), attorney use becomes 57.02% for trade marks (was 100%), 71.65% for designs (100%), 82.62% for
   patents (93.31%) and 41.21% for plant breeder's rights (52.22%); for overseas applicants it moves by under 4 points.
   It stays empty for provisional applications (ADR 0010). The label is now "An attorney or agent acts".
2. **`main_area` is for patents only.** For all 2,335,057 trade marks and 248,748 designs that had one, it equalled
   the main class (the Nice or Locarno class), so it is now empty for them, and the 57 patents with WIPO's
   `99_unknown` are empty too. `main_class` keeps every type's class; its note now says that a plant breeder's
   right's class is its plant genus.
3. **Two placeholder dates are emptied.** `retired_date` of 1 January 1970 (the zero of computer dates): 1,282 rights
   (1,279 trade marks, 3 designs), all filed from July 2013. `registered_date` before 1904, before the register's
   first application: 1 trade mark.
4. **A trade mark's days to registration are empty before 1986.** Of the 122,980 trade marks registered before 1986,
   121,207 (98.6%) were registered on the day they were filed: IP RAPID holds only the filing date for them (the
   finding behind ADR 0010's timeline start). Their `days_to_registration` (almost always 0) is empty; their
   `registered_date` is kept. Negative values fall from 1,497 to 57.
5. **An Australian applicant's missing state comes from the postcode.** IP RAPID leaves out the state for 34.96% of
   Australian standard patents filed from FY2024 and 13.65% of FY2023's (8.56% before), though their postcodes are
   recorded. Where both exist, the postcode's postal area (ASGS 2021, `abs_regions/poa`) is in the recorded state for
   99.41% to 100% of rights in every sub-type and period (98.54% to 100% for plant breeder's rights). So a missing
   state is filled from the postcode, and the 5 rights recorded as "queensland" become `qld`. Overseas applicants'
   states stay as recorded ("wa" for 3,135 overseas rights is most likely Washington); the state is read only for
   Australian applicants.

**Rejected.**
- **An attorney flag from the agent's client count** (an agent acting for five or more applicants). It is a useful
  bound, and the notebook shows it (49.52% for Australian trade marks against 57.02%), but a small firm's attorney can
  have few clients, and a business that files for related companies can have many. The client count stays a
  sensitivity check; the attorney firm itself comes with the parties attachment (B1).
- **Emptying the 57 remaining negative times or the 14 end dates after the build date** (to 27 April 2029). They are
  too few to matter, and nothing shows what the true values are.
- **Re-deriving `days_to_registration` from the earliest filing date.** For a PCT application that is the
  international filing date, so the measure would no longer be time in Australia's examination.

**Checked.**
- `tests/test_eda.py` checks that no right outside patents has a technology area, no placeholder date is left, no
  trade mark registered before 1986 has a time to registration, and every Australian applicant's state is one of the
  eight.
- `variables.yaml` notes say what each repaired column now means.
- The lens as built: 4,368,006 rows and 29 columns (unchanged). The other lenses do not read these columns.
