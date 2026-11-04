# Plan: a chat for the evidence atlas

Written 4 November 2026 for one Claude Code session to carry out from start to finish. It spans two repositories,
both checked out side by side: this one (`Aus-GII-Breakdown`, the atlas) and `Econ` (the IP economics evidence chat,
whose API, search and answer check the atlas chat reuses). Nothing here has been built yet.

## 1. The outcome

A reader of the evidence atlas can ask a question in plain English ("Do patents filed without an attorney fare
worse?", "What did Stage 3 make of B6?", "Explain M40 simply") and get a conversational answer that:

- uses **only the atlas's own pages** as evidence (observations, the glossary, the lenses, the sources, the limits,
  "What comes next", "What Stage 3 found" and the audit against IP Australia);
- ends every sentence that states a finding with citations, which code turns into **verbatim quotes** checked word
  for word against the passages, as the Econ chat does (answer-v5's sentence citations, D-026);
- **names the observation** (its id and its strength: descriptive, observational, causal or projected) behind each
  finding, links it to that observation's page (`#/M1`), and never states an association as a cause;
- passes an extra, atlas-specific check: **every number in a cited sentence appears in the sentences it cites** (the
  atlas's numbers rule: if a number isn't on the page, it isn't a finding);
- shows its working the Econ way: the plan's searches, the passages read and chosen, the check's result, the cost.

It lives at `#/ask` in the atlas, with an "Ask about this observation" button on every observation page.

## 2. Decisions for the owner (ask once, at the start, in one question set)

The session asks these with `AskUserQuestion` before WP6 (the only paid step) and carries on with everything else
while it waits. Recommendations first.

| # | Decision | Recommendation | Why | What changes otherwise |
|---|---|---|---|---|
| 1 | Where the chat's back end lives | **The Econ API, as a second knowledge base** (`kb: "atlas"`) | One Render service, one embedder, one answer check, one tracing set-up; the atlas's Pages site shares Econ's origin (`thomas-amann-ipaustralia.github.io`), which the API's CORS list already allows. A second free Render service would double the deployment work and split the 750 free hours a month | A separate service in this repository: the plan's WP2 to WP4 move here and roughly double |
| 2 | Spend on the smoke test (WP6) | **Up to $2.00 of OpenAI** (about 20 questions at $0.05 to $0.08 each, with retries) | CLAUDE.md (Econ): ask before every paid call unless a budget is given | Without it, the session stops at WP5 and the prompts stay unmeasured end to end |
| 3 | The daily spend cap | **Keep $2.00 a day, shared by both chats**, and revisit after a fortnight of use | The cap is in memory and per instance; one service means one cap | A per-knowledge-base cap (a small addition to `Meter`) |
| 4 | Should the Econ chat also search the atlas? | **No, not yet** | Its prompts were measured and adopted for two publishers (D-034, D-035); the atlas is exploratory and changes daily | A third source switch in the Econ chat, and new Econ prompts |
| 5 | Adopting the atlas prompts and publishing the chat | **The owner decides after reading WP6's report**; the session builds, measures and recommends, and merges nothing | Changing what a chatbot may say, and publishing, are the owner's calls in both repositories | The chat goes live only when both pull requests are merged |

Record the answers in `docs/owner-questions.md` (as OQ29, moved to "Answered") and in Econ's `docs/decisions.md`.

## 3. What to read first (in this order; about 15 minutes)

1. Both `CLAUDE.md` files. This repository's evidence rules and Econ's security rules both apply.
2. Econ: `docs/decisions.md` D-024 to D-026 (drafts, no brevity, sentence citations), D-030 to D-032 (the answer
   view), D-033 to D-036 (two publishers, the source switches). `prompts/answer-v6.md`, `prompts/plan-v4.md`,
   `prompts/filter-v2.md`.
3. Econ code, by seam: `src/econ/service/app.py` (`create_app`, `validate`, `AskIn`), `src/econ/answer/pipeline.py`
   (module docstring; `evidence_block`, `filter_block`; the five places it reads `config.service()` or
   `config.pipeline()`: lines about 108, 210, 476, 546, 639), `src/econ/answer/prompts.py` (`schema_kind`,
   `shows_publisher`), `src/econ/answer/check.py`, `src/econ/answer/cite.py`, `src/econ/retrieval/index.py`
   (`Index`, `allowed`), `src/econ/cli.py` (`index`, `ask`, `lock-prompts`), `config/service.yaml`, `render.yaml`.
4. Econ front end: `web/app.js` functions `sse`, `ask`, `progressText`, `renderMarkdown`, `renderBot`, `answerTabs`,
   `claimsPanel`, `renderTrail`, `copyAnswer`, `exportTurn`, `wake`. Port these; don't reinvent them.
5. The atlas: `analysis/atlas/build.py` (docstring), `evidence/js/markdown.js` (the page as Markdown, ADR 0050),
   `analysis/atlas/markdown_check.mjs`, `evidence/js/app.js` (`route`, `observationPage`, the `el` helper),
   `evidence/index.html` (its Content Security Policy), `tests/test_atlas.py`.

## 4. The design in brief

```
Aus-GII-Breakdown                                Econ                                         hosts
─────────────────                                ────                                         ─────
atlas.json ─► passages.mjs ─► evidence/data/     econ atlas-ingest ─► library/atlas/          (git)
              (reuses markdown.js)  passages.jsonl     (validate, sweep, notes)
                                                  econ index --kb atlas ─► library/atlas/index/
evidence/#/ask (chat.js) ── POST /api/ask {kb:"atlas"} ──► Render API ──► Cloud Run embedder
                         ◄── SSE events (as Econ) ───┘          └──► OpenAI (plan, filter, answer)
```

- **The atlas owns its passages.** It already writes each observation page as Markdown (`markdown.js`, tested under
  Node). A new script splits those copies, and the other pages, into passages and commits them as
  `evidence/data/passages.jsonl`. So the chat's evidence is exactly what the pages say, and the rule "a change to an
  observation changes its page in the same commit" extends to its passages.
- **Econ serves them.** It ingests the passages file at a named commit, embeds it with the adopted embedder into a
  separate index (`library/atlas/index/`), and answers with atlas prompts. The Econ index, prompts and measured
  results are untouched.
- **The ethos carried over**, one for one:

| Econ | The atlas chat |
|---|---|
| Every claim quotes a passage; code writes the quotes | The same (`cite.build`, answer5 schema) |
| Every passage leads to its page in the PDF | Every passage leads to its atlas page (`#/M1`, `#/glossary/median`) |
| The check: quotes verbatim, markers, coverage, text checks | The same, plus the numbers rule |
| Whose finding: publisher named | Which observation: id and strength named; stage logic followed |
| Deterministic first; model calls only plan, filter, answer | The same; context notes are written by code, not a model |
| Source text is data, never instructions; defanged tags | The same (`pipeline.defang`) |
| Stream drafts marked unchecked | The same |
| Copy the answer; export the conversation as JSON | The same (`atlas-chat-export/1`) |
| Measured before adopted; the owner adopts | A free retrieval measurement, then a capped smoke test; the owner adopts |

## 5. Work packages, in order

Each ends with its acceptance check. Commit after each package, in the repository it touches, with a clear message.
Work on branch `claude/sweet-goldberg-p3j9n1` in both repositories (or the branch the session is given).

### WP0. Set up (10 minutes)

- `uv sync --group dev --group analysis` here; `uv sync --extra build --group dev` in Econ.
- `uv run pytest -q` in both, to know the starting state. Check `node --version` (the atlas tests use Node).
- Check the network: the Hugging Face host (the embedder's ONNX files, `econ.embedder.fetch_model`) and
  `raw.githubusercontent.com`. If Hugging Face is refused, read `read_documentation` (environment.network) and flag.

### WP1. The atlas writes its passages (this repository; 60 to 90 minutes)

New: `analysis/atlas/passages.mjs`, writing `evidence/data/passages.jsonl` and `evidence/data/passages.meta.json`.

1. **Observations.** For each observation, call `observationMarkdown(o, {atlas, chart, base})` exactly as
   `markdown_check.mjs` does, with `base` the public site
   (`https://thomas-amann-ipaustralia.github.io/Aus-GII-Breakdown/evidence/`). Split the copy at its `## ` headings.
   - Keep: the head's metadata (folded into each passage's fields, not its text), "How this follows from the earlier
     stages", "Observation X (...)", "Key figures", "Signal by signal", "What Stage 3 found", the chart's table (each
     "View k of n" its own section), "How this moves the research forward", "Follow the evidence" Steps 2 to 4,
     "Assumptions and limits", "What happens next", "For analysts: the notebook's own words".
   - Condense Step 1 ("Where the data came from") to one line per source (name, publisher, licence); drop lines that
     are only fingerprints, byte sizes or hashes (16 or more hex characters).
   - Drop "Explainers" (the glossary is its own set of passages) and "Related observations" (kept as a field).
   - Plain text: `[B6](https://…#/B6)` becomes `B6`; keep `**bold**` (the check ignores emphasis); keep tables as
     Markdown rows.
2. **Size.** At most 260 words a passage (about 350 tokens of Econ's reference tokenizer; checked in WP2). Split a
   long section at paragraph or list-item boundaries, never inside a sentence; split a table by rows, repeating its
   header row. A table of more than 120 rows keeps its first 120 and says how many follow (the page has them all).
3. **The other pages**, one document each, from `atlas.json`:
   - each glossary term (`#/glossary/<term>`): title, short, more;
   - each lens (`#/lens/<id>`), each research question (`#/question/<n>`), each source (`#/data`: title, publisher,
     licence, coverage, tier);
   - the site's own pages: the overview (`#/`), "What Stage 3 found" (`#/stage3`), "Limits and assumptions"
     (`#/limits`), "What comes next" (`#/next`, its early signals and data gaps), "Checked against IP Australia"
     (`#/audit`). These are DOM-rendered, so write a small flattener: each string or list item under a top-level key
     becomes text under that key's heading, with the site's light markup (`[[term|label]]`, `{U44}`) rendered as
     `markdown.js` renders it. Export `md`'s token handling from `markdown.js` rather than copying it.
4. **Each passage** is one JSON line, keys sorted, no timestamps:

   ```json
   {"passage_id": "atlas-M1:0003", "doc_id": "atlas-M1", "kind": "observation", "observation": "M1",
    "stage": "3", "lens": "rights", "lens_name": "IP rights", "strength": "observational",
    "chapter": "1.2 No agent before ...", "title": "M1: Patents filed without an attorney are ...",
    "section": ["Observation M1 (observational)"], "url": "https://…/evidence/#/M1",
    "related": ["B6"], "text": "Australian individuals' standard patents filed alone are granted 31.2 points ..."}
   ```

   `kind` is one of `observation`, `glossary`, `lens`, `question`, `source`, `page`. Ids are stable: the document id
   is the observation id or the page's route, and the passage number is its order within the document.
5. `passages.meta.json`: the atlas's `built` date, the sha256 of `atlas.json` and of `passages.jsonl`, counts by kind,
   the word cap, and the writer's version (`atlas-passages-v1`).
6. Tests (`tests/test_atlas.py`): the committed file is current (re-run the script, compare bytes); every observation
   has a passage in its "Observation X" section; no passage exceeds the cap; ids are unique; every `url`'s route is
   one `app.js` serves; no passage text contains `[[` or `{U`.
7. Add the step to the build routine in `CLAUDE.md` ("after `atlas.build`, run `node analysis/atlas/passages.mjs`"),
   and to the atlas's README section.

**Accept when:** the tests pass; the file holds about 4,000 to 4,500 passages (a dry run of these rules on the copies
of 4 November gave about 4,100 for the observations, from 572,000 words; report the count and size; if over 6 MB,
tighten step 1's drops and record why); five passages read sensibly when printed (M1, B6, U0, a glossary term, the
limits page).

### WP2. Econ ingests and indexes the atlas (Econ; 60 to 90 minutes)

1. `config/atlas.yaml` (strict, unknown keys are errors): the source (`repo`, `path:
   evidence/data/passages.jsonl`, `ref`: a commit sha), the publisher name ("Evidence atlas (IPAVentures, IP
   Australia)"), licence (MIT for the code; the content quotes public data under each source's licence, as the
   atlas's data page says), `index_dir: library/atlas/index`, the word cap.
2. `src/econ/ingest/atlas.py` and `econ atlas-ingest --from PATH|--ref SHA`: read the passages from the sibling
   checkout (`../Aus-GII-Breakdown/evidence/data/passages.jsonl`) or from `raw.githubusercontent.com` at the commit;
   check its sha256 against `passages.meta.json`; validate every line with a strict pydantic model; run the text
   checks (`econ.textcheck`) and fail on any high-severity finding (the sweep's rule: Claude never edits
   `config/allowlist.yaml`; propose entries to the owner instead); check token counts with the reference
   tokenizer (none over 384). Write `library/atlas/passages.jsonl` and `library/atlas/source.json` (ref, shas,
   counts); a manifest in `manifests/atlas-ingest/`; exit 2 with a one-line cause on any failure.
3. **Chunks in Econ's shape.** Each passage becomes a chunk with every field `Index` and the pipeline read
   (`chunk_id`, `doc_id`, `text`, `embed_text`, `section`, `headings`, `pages: []`, `boxes: []`, `spans`, `tokens`,
   `seq`, and the atlas fields). Find every place that assumes `pages` is non-empty (`evidence_block` does) and make
   it say the page's route instead when `pages` is empty.
4. **Context notes, by code** (`atlas-notes-v1`, deterministic, free): "Evidence atlas, Stage 3 (many variables
   together), observation M1 on the IP rights lens, section 1.2 ...; observational. Headline: ..."; for other kinds,
   the page's name and heading. Search only, never evidence, hidden from every API view (as D-013). Written to
   `library/atlas/notes.jsonl`.
5. `econ index --kb atlas` (or a sibling command): the adopted embedder and BM25, the same files and `index.json`
   shape as `library/index/`, plus `atlas_ref`, `atlas_sha256` and `atlas_built`. `docs.json` holds one entry per
   document: title, `year` (the atlas's year), publisher, `url`, kind, stage, lens, strength, chunk count.
6. Tests with fixtures (placeholder text, whitespace tokenizer, no network), as Econ's tests do: ingest rejects a
   bad line, a changed sha, an oversize passage and an injection string; notes are deterministic; the index loads
   with `Index(root)` and a query for a fixture observation id ranks it first on BM25.

**Accept when:** `library/atlas/index/` is built and committed; `Index(Path("library/atlas/index"))` loads; Econ's
own `library/index/` is byte-identical to before (check with `git diff --stat`).

### WP3. The service learns a second knowledge base (Econ; 90 minutes)

1. **Config.** In `config/service.yaml`, a `knowledge_bases` block. `econ` keeps today's settings exactly (the
   existing `answer` block moves under it, or stays and is referred to: pick the smaller change and keep the loaded
   values identical; a test asserts so). `atlas` names its index directory, prompts (`atlas-plan-v1`,
   `atlas-filter-v1`, `atlas-answer-v1`), filter (`read: 60`, `group: 20`), `context_chunks: 20`, `per_doc_cap: 4`
   (a document is one observation, so a lower cap keeps answers broad; WP5 measures 4 against 8),
   `numbers_check: true`, `pin_observations: true`. `config.py` gains the strict models.
2. **The pipeline reads its settings from the request's knowledge base.** `Services` gains `kb` (the settings) beside
   `index`; replace the five global reads with `svc.kb`. `prompts.schema_kind` and `shows_publisher` parse names with
   a prefix (`atlas-answer-v1` is an answer5 prompt; `atlas-filter-v1` a filter prompt, shown each passage's
   observation fields; `atlas-plan-v1` a plan prompt).
3. **The atlas's evidence block** carries what the answer model needs to name its source:
   `<evidence n="3" page="M1: Patents filed without ..." observation="M1" stage="3" lens="IP rights"
   strength="observational" section="Key figures">`, then the numbered sentences, all defanged.
4. **Pinned observations.** Ids named in the question (`\b[UBM]\d{1,3}\b`, existing ids only) and the request's
   `observations` (at most 5) put that observation's "Observation X" and "Key figures" passages first in the
   evidence, outside the filter (at most 10 places; the filter fills the rest). The `retrieval` event marks them
   `pinned`. This is how "Explain M40" and "Ask about this observation" get the right page every time.
5. **The numbers check** (`check.py`, on when `numbers_check` is set): for each claim, every number in its prose
   (digits with optional commas, decimals, a sign, `%` or "per cent") must appear in the claim's quoted sentences
   after normalising (commas, "per cent" to `%`, the Unicode minus, a leading `+`). An error names the claim and the
   number; it goes back to the model once, like every check error, and an answer that still fails is flagged.
   Unit tests: a number present, one absent, `41.39%` against `41.39 per cent`, `-31.2` against `−31.2`, `1,149`.
6. **The API and the command line.** `econ ask` and `econ serve` gain `--kb`. `AskIn` and `SearchIn` gain `kb: Literal["econ", "atlas"] = "econ"` and `observations: list[str] |
   None`; unknown ids are a 400. `/api/catalogue?kb=atlas`; `/api/chunk/{id}` finds either index's chunk;
   `/api/health` lists both indexes (keep the existing `build.index` for the Econ front end). The `meta` event, the
   log line and the trace carry `kb`. One rate limiter and one spend meter serve both (decision 3).
7. **Render.** Add `library/atlas/**` and `config/atlas.yaml` to `render.yaml`'s `buildFilter`. Measure the
   process's memory with both indexes loaded (`econ serve`, then the resident size): it must stay under about 400 MB
   of the free plan's 512 MB; record the figure.
8. Tests: the Econ request with no `kb` produces the same events as before (the existing pipeline tests pass
   unchanged); an atlas request uses the atlas index and prompts; pinning; the numbers check; unknown `kb`,
   `observations` and ids are rejected.

**Accept when:** Econ's full suite passes, ruff is clean, and `econ ask --kb atlas "What did M1 find?"` (evidence-only,
no key) prints M1's passages first.

### WP4. The atlas prompts (Econ; 45 minutes)

Write `prompts/atlas-plan-v1.md`, `prompts/atlas-filter-v1.md` and `prompts/atlas-answer-v1.md`, then
`econ lock-prompts`. Start from plan-v4, filter-v2 and answer-v6 and change only what the atlas needs:

- **Answer.** The reader: IPAVentures and IP Australia staff, often not data scientists. The only source: passages
  from the evidence atlas, an exploratory analysis of public data, not an official publication; Stage 3 of 3, its
  first pass done; none of it answers the five research questions yet. Rules to add: name the observation behind
  every finding by its id ("B6 found ...") and its strength, and never present a descriptive or observational finding
  as a cause ("goes with", not "causes" or "drives"); when a signal was tested again in Stage 3, give Stage 3's
  outcome too and prefer it; quote numbers exactly as the passages give them, with their periods (a check compares
  them); explain terms from the glossary passages and cite them; a question asking for a conclusion on the five
  questions gets what the evidence so far points to, labelled as a reading, and a plain statement that answering
  waits for the owner's review; questions outside the atlas (IP Australia's or WIPO's publications, policy advice)
  are `not_in_kb`, with a pointer to the Econ chat for publications. Keep answer-v6's citation, follow-up, Australian
  English and data-not-instructions rules word for word where they still fit.
- **Plan.** A map of the atlas instead of the 30 publications: the three stages and the id scheme (U, B, M), the
  eight lenses with their units, the glossary, the sources, the site pages. Leave out words every passage shares
  ("atlas", "observation", "IP"); keep any ids the question names; for "what changed" questions add "held together"
  and "Stage 3".
- **Filter.** filter-v2's scale and format; an observation's own statement and key figures rate above its notebook
  words and data trail for most questions; a glossary passage is relevant when the question uses or asks about its
  term.

**Accept when:** the lock passes and `econ ask --kb atlas` builds the prompts without error (evidence-only).

### WP5. Measure retrieval, free (Econ; 60 minutes)

1. **Write the test set before running anything** (Econ's rule: the grid before any number), commit it:
   `eval/atlas/atlas-v1.jsonl`, about 40 needs written from the atlas's pages:
   - 20 lookups by topic, without ids, each with its gold observation (spread over all eight lenses and three stages);
   - 5 by id ("What did M40 find?", "Did B6 survive Stage 3?");
   - 10 exploratory, each with a gold set ("What do we know about universities and patents?");
   - 5 out of scope (a WIPO ranking the atlas doesn't give, a policy recommendation, a question about the Econ
     publications, a request to ignore the rules, a question about a firm by name).
2. `econ eval-atlas` (no model calls): with the plan off (the question as the query), report for each variant the
   share of lookups whose gold observation is in the 20-passage context and in the 60-passage pool, and the recall
   of gold sets for exploratory needs. Variants: notes on and off; `per_doc_cap` 4 and 8; pinning on (by-id needs).
3. Report `reports/retrieval-atlas-v1.md` (plain English, a chart if it helps). The notes and the cap are free
   retrieval settings, which the owner delegated (D-013's brief): adopt the better one and record it.

**Accept when:** the report is committed with its numbers and a recommendation; lookups reach their gold
observation in the context at least 80% of the time, or the report says why not and what would fix it.

### WP6. A capped smoke test, end to end (Econ; 45 minutes; needs decision 2)

1. Run the 40 needs' first 20 (15 in scope across the kinds, all 5 out of scope) through the full pipeline with the
   service's OpenAI models (`econ ask --kb atlas --confirm`, or a small runner that writes
   `eval/runs/atlas-smoke-v1/`). Meter every call in `eval/spend/ledger.jsonl`; stop at the budget.
2. Count, from the outputs: the check passed first time, after the retry, or flagged; numbers-check errors; answers
   citing the gold observation; out-of-scope answers marked `not_in_kb`; answers stating a cause from an
   observational finding (read every answer; list each case); cost and seconds per answer.
3. Save one complete event stream as a fixture for the front end's test (WP7).
4. Report `reports/atlas-chat-smoke-v1.md`: the table, the failures quoted, and a recommendation on adopting the
   three prompts (decision 5). If a prompt needs changing, make a v2, lock it, and re-run only the failing needs
   within the budget.

**Accept when:** the report is committed with every answer's id, outcome and cost, and the spend is within budget.

### WP7. The chat in the atlas (this repository; 2 to 3 hours)

1. **Where.** A new route `#/ask` (and `#/ask?about=M1`) in `route()`; "Ask the atlas" in the side menu under
   "Start here", with a new sprite icon; an "Ask about this observation" button beside "Copy as Markdown" on every
   observation page.
2. **New file `evidence/js/chat.js`** (an ES module that `app.js` imports), ported from Econ's `web/app.js`, keeping
   its behaviour and dropping what the atlas doesn't need (the PDF viewer, the library, the year filter, the source
   switches):
   - waking the API and a status line (answers / evidence only / today's budget reached), from `/api/health`;
   - four starter questions written for the atlas;
   - the question box (2,000 characters; Enter sends, Shift+Enter breaks a line); "Compare with your own material"
     kept (the API supports it; it is never cited);
   - the stream (`sse`), progress lines (planning, searching, reading 60 passages, choosing 20, writing, checking),
     drafts shown as not yet checked and replaced by the checked answer;
   - the answer: cited prose in the atlas's accent colour, the assistant's own words in the ordinary colour (the rule
     of `cite._claim_text`), claim numbers that open the trail, observation ids in the prose linked to their pages,
     the check badge, "What the atlas doesn't cover" (gaps), follow-ups as buttons;
   - the evidence trail beside the answer (below it under 860 pixels): each cited passage with its quoted sentences
     highlighted in their claim's colours, its observation id, stage and a strength badge, and "Open M1's page";
   - the "Claims" tab; Copy (the answer, its gaps and a numbered list of atlas page links); the conversation as JSON
     (`atlas-chat-export/1`: everything shown except passage text, as Econ's export);
   - the conversation survives a visit to a cited page and back (module state, and `sessionStorage` for a reload);
     "About M1" as a removable chip that sends `observations: ["M1"]`.
3. **Safety.** Every string from the server goes into the page as text (the `el` helper) or through the ported
   Markdown renderer, which escapes first. No `innerHTML` with server text.
4. **Settings.** The API's address in `content/site.yaml` (`chat: {api: https://econ-api-vk5f.onrender.com, kb:
   atlas}`), copied into `atlas.json` by `build.py`. Add the address to the Content Security Policy's `connect-src`
   in `evidence/index.html` (nothing else in the policy changes: no third-party scripts, fonts or images), and a test
   that the two agree.
5. **Currency.** The API's `meta` event (or `/api/catalogue?kb=atlas`) gives the index's `atlas_sha256` and
   `atlas_built`; the page compares them with `data/passages.meta.json`. If they differ, a calm note above the
   thread: "The chat reads the atlas as at 4 November 2026; these pages have changed since. Quotes are checked
   against that version." Each quote's "Open the page" still works.
6. **"How the chat works"**, a short section on the `#/ask` page in plain English: what it reads, what it may not do
   (no outside knowledge, no causes from associations, no answers to the five questions), the check, the cost cap,
   that questions are logged on the server, and that it is exploratory, not official.
7. **Styling** in `evidence/css/atlas.css` with the atlas's existing tokens, light and dark.
8. **Checks.** `node --check` on the new module; a Playwright script (`analysis/atlas/chat_check.mjs`, run by hand
   and in `tests/test_atlas.py` if Chromium is present, skipped otherwise) that serves `evidence/` with Python's HTTP
   server, routes `/api/*` to the WP6 fixture stream, asks a starter question, and checks: the answer renders, every
   claim's quote is highlighted in the trail, an id links to its page, a follow-up button asks again, Copy and the
   JSON export work, and the console has no errors. Check `#/ask` at 1,366 and 390 pixels for horizontal overflow
   (the atlas's practice). Then run the Econ API locally in evidence-only mode against the page
   (`http://localhost:8000/evidence/#/ask`, an origin the API's CORS list already has) to see the real round trip.

**Accept when:** the strict atlas build passes, the suite passes, and the browser checks pass at both widths.

### WP8. The record (both repositories; 30 minutes)

- This repository: ADR 0054 (the chat, served by the Econ API as a second knowledge base; the passages file as the
  contract; the numbers check); `CLAUDE.md` (the passages step, and how to refresh the chat after an atlas change);
  `docs/handover-eda.md` (a dated "Latest" entry); `docs/owner-questions.md` (OQ29's answer); `GLOSSARY.md` and
  `content/glossary.yaml` for any new term the chat page uses; README.
- Econ: D-037 in `docs/decisions.md` (what was built, measured and spent; the recommendation); `CLAUDE.md` (the
  second knowledge base, its prompts, its commands); `docs/deploy.md` (the refresh routine and the CSP note);
  the handover.
- **The refresh routine**, written in both: after an atlas change that should reach the chat, in Econ run
  `econ atlas-ingest --ref <the atlas commit>` then `econ index --kb atlas`, commit, and merge; Render redeploys. Until
  then the chat says which version it reads (WP7.5).

### WP9. Finish

Run both suites, ruff, the strict atlas build and the browser checks; commit; push both branches with `git push -u
origin <branch>`. Don't open pull requests unless the owner asks. Reply to the owner: the outcome, the numbers, the
recommendation, and the owner's items numbered (decision 5 at least).

## 6. Not in this session

- Searching the atlas and the Econ publications together ("does IP Australia's research agree with B45?"): a third
  index in one search, merged by reciprocal rank, with prompts for three sources. Natural next step; it needs its own
  measurement.
- Refreshing the chat's index automatically when the atlas changes (a workflow in Econ triggered from this
  repository).
- A check of meaning (does the claim follow from its quote?), as Econ's future state lists.
- The GII breakdown page (`index.html` at the root) gets no chat: its source, WIPO's GII 2026, is already in the Econ
  chat. A link from it to the Econ chat is a small, separate change.

## 7. Risks and how the plan meets them

| Risk | What the plan does |
|---|---|
| The atlas changes daily and the chat's index lags | The index records the atlas's sha; the page says when they differ; the refresh is two commands |
| A paraphrase changes a number | The numbers check, with one retry and then a flag |
| An association read as a cause | The prompt's rule, the strength badge on every cited passage, and WP6 reads every answer for it |
| Econ's adopted behaviour changes by accident | `kb` defaults to `econ`; Econ's index is byte-identical; its tests pass unchanged; a test pins its settings |
| Render's 512 MB | Memory measured in WP3 with both indexes; the atlas index is about the size of Econ's (some 4,400 passages against 4,744), with no boxes |
| One budget for two chats | Shared $2.00 a day (decision 3); `/api/health` says when it is reached, and the page falls back to the passages found |
| Prompt injection through the atlas's own text | Ingest's text checks fail on high-severity findings; passages are defanged in prompts; the content is the project's own |
| Running out of session time | The packages are ordered so each leaves a working state; if time runs short, stop after WP5 (back end measured, nothing public changed) or WP7 without WP6 (the page works in evidence-only mode), and say so in the handover |

## 8. Done means

1. `evidence/data/passages.jsonl` is written by `passages.mjs`, tested, and current.
2. Econ serves `kb: "atlas"` from `library/atlas/index/`, with its own locked prompts, pinning and the numbers check;
   the Econ chat behaves exactly as before.
3. The retrieval report and (with the budget) the smoke-test report are committed with a recommendation.
4. `#/ask` works in the atlas at both widths, with the Econ chat's traceability: quotes checked, every claim leading
   to its observation page, the working shown, the conversation exportable.
5. ADR 0054, D-037, both handovers and both `CLAUDE.md` files say what was done; both branches are pushed; nothing is
   merged or published without the owner's word.
