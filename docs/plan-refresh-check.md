# Backlog: a check that carries a data refresh through the atlas

**Status:** proposed, not built (11 November 2026). The owner asked for suggestions (A42): "I'm reluctant to conduct any
re-runs as that may require amendments to the observational prose. Do you have any suggestions for how we can
automate a check to ensure any updates are captured and effectively diffused through the atlas?" Building it is the
owner's call (OQ38).

## The problem

When the data under an observation change, three things can go wrong, and today only the first is caught:

1. **Nobody notices.** Caught: the currency check's fingerprint includes each source's data files, and the build asks
   for the cells to be re-run or a reason recorded (ADR 0058 addendum).
2. **The cells are re-run, the outputs change, and the prose still quotes the old numbers.** Not caught. The numbers
   rule checks the atlas against the notebook's page, and the page includes the prose, so an old number that is still
   in the prose passes.
3. **The prose is updated, and something further along still quotes the old number**: the plain-English reading, the
   atlas's figures and chart, a relation, a summary on the overview. Mostly caught: the numbers rule fails each
   observation field once the number has left the page. The site's own pages (summaries, early signals) are not under
   the rule.

A fourth is a blind spot today: **a new source or a change to the lens code disturbs an existing column** (a join that
repeats rows, say) without any existing source file changing. The fingerprint does not see it.

## What was measured

On the three notebooks as they stand (231 observations, 11 November 2026). The prose quotes 5,594 substantive numbers
(years and one- or two-digit counts set aside). Of the notebooks' outputs, 466 are tables, 175 printed text and 114
charts.

| Where the quoted number is, in the outputs above its observation | Numbers | Share |
|---|---:|---:|
| At exactly one place (one table cell or one printed line) | 3,916 | 70.0% |
| At several places (the same value in more than one cell) | 724 | 12.9% |
| A rounded or percentage form of a value there | 549 | 9.8% |
| Not there: from another observation, worked out by arithmetic, or read off a chart | 405 | 7.2% |

So about 93% of the numbers the prose quotes can be traced to a place in an output by code. The other 405 need a note
written once saying where each comes from (the audit of 10 November explained each of these by hand, ADR 0057).

## The suggestion: bind each quoted number to its place, then re-run in a copy

1. **Fingerprint the lens tables, column by column**, when they are built (a hash and a row count for each column,
   in a small committed file). An observation's check then rests on the columns its cells read. This closes the blind
   spot: a new source that leaves the old columns alone flags nothing, and one that disturbs them flags exactly the
   observations that read them.
2. **Bind.** One pass writes, for each observation, where each quoted number sits: the cell, the table, the row's
   label and the column's label (labels, not positions, so a new year's row does not shift everything), and how it
   is written (rounded, or as a percentage). About 93% by code; the 405 others by hand, once.
3. **Re-run in a copy, never in place.** After a refresh, a tool runs each notebook in a scratch folder and reads the
   new value at every bound place. The reviewed notebooks are not touched.
4. **Report the drift**, observation by observation:
   - *nothing moved*: confirmed automatically, with the evidence; no prose is touched;
   - *numbers moved*: each listed as old and new ("10,069, now 10,412");
   - *a place is gone* (a row or column no longer exists): flagged for a person.
5. **Carry it through.** For an observation whose numbers moved, the tool drafts the change: the new numbers in the
   notebook's prose with a dated note quoting the old ones, and the same substitution in the reading, the atlas's
   figures and its chart. The numbers rule then refuses anything that still quotes an old value, and the currency
   check runs because the words changed. Extend the numbers rule to the site's own summaries (a number in an item
   that names observations must be on one of their pages).
6. **A tripwire for the words.** A moved number is flagged for judgement, not just substituted, when it crosses
   something the prose asserts: a direction reverses, a likely range now includes no difference (or stops including
   it), a Stage 3 outcome's threshold is crossed (ADR 0046), or a word such as "doubled", "most" or "half" no longer
   fits.

Steps 1 to 4 change nothing in the notebooks or the atlas. They answer the question behind the reluctance: *how much
would a refresh actually move?* Only then is step 5 run, and only for the observations on the list.

## A policy that goes with it

Treat a refresh as a release, not an event: the atlas already shows the date each source was copied (step 1 of every
page's trail). Refresh on a schedule or for a reason, read the drift report, and decide. Between releases every
observation is current as at its data's date, which the page states.

## Cost and risks

- **Effort:** about one session for steps 1 to 4, another for 5 and 6. Free: no paid service.
- **Run time:** a full run of the three notebooks against the lens tables from R2; not yet timed in this environment.
- **Risk:** a binding by label breaks if a table's layout is rewritten; the tool reports it as "a place is gone"
  rather than guessing.
- **Not covered:** numbers that exist only in a chart (114 charts) unless the cell also prints them; the 405 numbers
  from elsewhere, until their notes are written.
