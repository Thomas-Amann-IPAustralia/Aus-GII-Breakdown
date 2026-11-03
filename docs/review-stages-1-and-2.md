# Review of Stages 1 and 2: quality assessment

**Date:** 2 November 2026 (pass 8, ADR 0043). **Scope:** every observation of `analysis/notebooks/01_univariate.ipynb`
(U0 to U123) and `02_bivariate.ipynb` (B1 to B62), read against the outputs above it; both notebooks re-run from a fresh
build; `docs/stage-1-summary.md` and `docs/stage-2-summary.md` checked number by number; the full Stage 2 audit's open
findings (`analysis/claude-audit/261102/`) checked and acted on where they held. The record, finding by finding, is pass
8 in `analysis/GPT-audit/261030/AMENDMENTS.md`.

## Verdict

**Both stages are sound, transparent and reproducible, and after this pass they are fit to publish.** The figures were
almost always right: what needed correcting was mostly what they were taken to show. Stage 1 is a careful descriptive
profile with small slips. Stage 2's method is good (a screen with a correction for many tests, a second sample, effect
sizes with intervals, named third factors), but its prose often read further than its numbers, and one denominator was
wrong. The summary documents had fallen further behind the notebooks than the notebooks had behind their outputs.

| | Stage 1 (univariate) | Stage 2 (bivariate) |
|---|---|---|
| Observations restated in this pass | 31 of 124 (25%) | 37 of 62 (60%) |
| Figures that did not match the page | 17, nearly all small (a stale count, a rounded display read as exact, a range misread) | 9 (among them B37's heading, B38's range across a break, B39's misread row) |
| Readings beyond the evidence | 13 (a heading broader than its bullets, a cause or a mechanism from a description) | 26 (absences from weak correlations, same-unit "replications", "file" for allocated counts, mechanisms) |
| Selection errors | 1 (U112) | 2 (B50, B51: the same one) |
| Reproducibility | Same outputs from a fresh build; two tables' row order varied (now sorted) | Identical outputs; one table's row order varied on a later run (now sorted) |
| Consistency with later data | Good, after seven passes; a few lags (U1's column count, U11's settled lead, §9's rows) | Good; §1's expedite rule was still Stage 1's first (now U103's) |

## What was wrong, by kind

1. **Small factual slips** (most corrections): a count left short (U3), a share mis-added (U9: designs 25.5% in force,
   not 24%), a peak the same table contradicts (U38), a range read from selected years (U5, U84, U86), values read
   from pandas' rounded display (U65, U70), a statistic misnamed (U41), stale rows in the section summaries.
2. **Readings broader than the output**: "not lower for any type" (U6), "not from businesses" (U8), "less of both"
   (U47), "every candidate break" (B37, one of eight is ordinary), "within every kind of entity" (B24).
3. **Weak or untested associations written as facts or absences** (the main Stage 2 theme): "does not lift its
   filing" (B59), "raising R&D would not ... raise patenting" (B34), "no link" (B45), "do not move together" (B36,
   B39), "rise together in booms" (B52), "a fair sign of commercialisation" (B62). Restated as "no association detected"
   or as hypotheses.
4. **What a count measures**: industry counts are applications allocated by technology, mostly overseas applicants',
   not what a division's businesses file (B40 to B60); US patents' citations are not where Australian research is used
   (U85, B46); "patents are filed by manufacturers" contradicted Stage 1's own rule (B31).
5. **One selection error**: shares of WGEA employers that file were taken among those the firms lens holds, which
   leaves out every employer with no IP, R&D, procurement or tax record. Over every employer the share with a filing
   linked is 48.6% to 72.9% by size, not 70.4% to 82.5%, and the size gap for any filing doubles (24.3 points).

## What holds up to expert scrutiny

- **Every number quoted is on the page**, or is arithmetic on it, a chart's label or a cross-reference, from outputs a
  fresh build reproduces. The exceptions are context, not findings: a few fee amounts from the fee schedules (U110)
  and Australia Post's postcode ranges (U49).
- **The limits are stated where the findings are**: lifetimes as shares still in force, not value (U36); first
  observed filing, not entry (U101); two ownership endpoints, not transfers (U18); allocated industry counts (U75);
  places and countries as ecological associations (§3, §4); gender estimates for inventors in Australia only (U97).
- **Corrections are traceable**: each is dated where it is made, with the earlier wording, and recorded with its
  check in `AMENDMENTS.md` and an ADR.

## What an expert could still challenge (residual risks)

1. **Data coverage the project cannot fix alone**: IP RAPID's missing ABNs since FY2025 (OQ7), Google Patents' older
   Australian families (B55, OQ21), inventors' countries for patents filed only in Australia (U95), an institutions
   link no one in the sector has reviewed (OQ11), and `agent_first_date`, a batch date for a third of patents (U40).
2. **Inference not yet upgraded**: intervals from 100 resamples of rows treated as independent; serially dependent
   quarterly changes (§5); small lenses of 19 divisions, about 110 institutions and 36 OECD members, whose "second
   samples" are the same units; crosswalk allocation by technology; citations from US patents only.
3. **Leads, not findings**: the provisional surge (U8, B38), direct filing (U90), the first-patent-filer fall after
   August 2021 (U45), plant breeder's rights' recent low (U6). Each needs IP Australia's records or Stage 3's designs.

## For Stage 3 (methods the audit proposed, not done here)

Block bootstraps or effective sample sizes for §5's changes; 1,000 or more resamples for any interval that is quoted;
B42 and B60 through the crosswalk with services; fixed-age windows for citations (B44 to B46); research expenditure as
an exposure for B62; the window-free within-firm order for B25 and the party-aligned filer for B30; heatmap legends;
and partial correlations or models that hold the named third factors together, as the plan already intends.
