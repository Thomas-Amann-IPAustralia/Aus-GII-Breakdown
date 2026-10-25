# 0016: The firms lens counts applications by the filer, keeps what each firm holds, and flags IPLORD-only firms

**Date:** 2026-10-25. **Whose:** Claude's (the owner asked for the `firms` lens next, 2026-10-25); the owner can
overturn any of it. It carries out the switch that ADR 0013 set for this lens, and records three repairs found while
profiling it. The evidence is in `analysis/notebooks/01_univariate.ipynb`, section 2 (observations U41 onwards).

**Context.** The lens credited each right to the first *current* applicant with an ABN, so a firm's application counts
described what it holds now, not what it filed (ADR 0013, N02). Profiling the lens also found ABNs that are in it only
because IPLORD links them to IP, with no sign of that in the lens; states left blank by the ABR; and one postcode in an
ABS area of people with no usual address.

**Decision.**
1. **Applications by the filer.** `n_patents_standard`, `n_patents_provisional`, `n_patents_second_tier`,
   `n_trade_marks` and `n_designs` count the rights whose first founding applicant with an ABN (`founder_abn`) is this
   firm. Where both ABNs are known, the filer is not the holder for 2.17% of standard patents and 7.11% of trade marks;
   58,676 firms' trade mark counts and 6,118 firms' standard patent counts change. For patents filed before FY2003 the
   founding applicant may be a later holder (ADR 0013).
2. **What each firm holds, beside it:** `n_held` (rights of every type and status whose first current applicant with
   an ABN is this firm) and `n_held_in_force` (of those, in force, from ADR 0015). These are a different measure from
   the filing counts and are never added to them.
3. **`in_iplord`.** IPLORD (to FY2020) links 52,949 of the lens's ABNs to trade marks, designs or plant breeder's
   rights that IP RAPID gives no ABN for; 50,790 of them are in the lens through IPLORD alone, with 0 in every IP count.
   The flag says so. IPLORD's counts are not brought in: they are built differently (for ABNs in both, 81.0% agree
   with IP RAPID's applicant panel, but the largest filers' counts run up to 7 times higher, and IPLORD's weighted
   total is less than half of IP RAPID's), and the plan uses IPLORD only to check IP RAPID before 2020.
4. **State and remoteness.** The ABR leaves the state blank (an empty string) for 3,977 ABNs; it is now empty, and
   filled from the postcode's postal area where there is one (165). Remoteness is empty for an ABS area of people with
   no usual address (one firm).

**Use.** "Who files" uses the `n_*` counts and `ip_filed_total` (every founding applicant) or `ip_filed_weighted`
(shared applications split); "who holds" uses `n_held` and `n_held_in_force`. IP counts for firms are lower bounds:
they cover only rights IP RAPID links to an ABN, and the share of Australian organisations' trade marks with a filer's
ABN falls from 84.1% (FY2024) to 59.9% (FY2026), so firm-level filing by year is compared to FY2024 until the cause is
known (U45).

**Rejected.**
- **Keeping holder-based counts per type.** Two per-type measures of "applications" would invite adding or mixing
  them; one total of rights held, and one in force, answer "who holds".
- **Adding IPLORD's counts to IP RAPID's,** or using them for the IPLORD-only firms. Their definitions differ (above),
  so a sum would mix measures.
- **Dropping the IPLORD-only ABNs.** They are firms that used the IP system; dropping them would make the lens look
  more complete than it is.

**Checked.**
- `tests/test_eda.py`: the filing counts sum to the rights with a filer's ABN; no firm holds more in force than it
  holds; every state is one of the eight or empty; no remoteness of "no usual address".
- The lens as built: 398,450 rows and 40 columns (37 before, plus `n_held`, `n_held_in_force` and `in_iplord`). The
  `regions` lens, which reads `firms`, is rebuilt and unchanged in shape.
