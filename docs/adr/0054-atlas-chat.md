# 0054: A chat for the evidence atlas, served by the Econ API as a second knowledge base

**Date:** 2026-11-04. **Whose:** the owner's (what: OQ29, answered A37, with the condition that it feel like a separate
service from the Econ chat, in the atlas's own look); Claude's (how), which the owner can overturn. The plan is
`docs/plan-atlas-chat.md`; the Econ repository records its side as D-037 and D-038.

**Context.** Readers of the atlas want to ask it questions in plain English. The Econ repository already runs a chat
whose every claim quotes a passage that code checks word for word. The owner asked for the same here, kept apart from
the Econ chat in what it searches and how it looks.

**Decision.**

1. **The atlas owns its passages.** `analysis/atlas/passages.mjs` splits every page into passages and commits them as
   `evidence/data/passages.jsonl` with `passages.meta.json` (atlas-passages-v1). Observation pages come from their
   Markdown copies (`evidence/js/markdown.js`, which now exports its markup handling, output unchanged), so a passage
   says exactly what its page says; the glossary, lenses, research questions, sources and the overview, Stage 3,
   limits, next and audit pages are flattened from `atlas.json` with the same markup. Each passage is at most 260 words
   and, by an estimate of Econ's reference tokenizer, 360 tokens (numbers and codes tokenise at up to 4.6 tokens a
   word, so a word cap alone let 631 passages exceed the 384 Econ's chunks keep to; by the tokenizer itself the largest
   is now 338). Step 1 of an observation's trail is one line per source; table sizes, fingerprints and hashes are
   dropped; the explainers and related observations are left out (the glossary is its own passages). 4,611 passages
   from 454 pages, 5.5 MB. The file is the contract: a test checks it is current, so "a change to an observation
   changes its page in the same commit" now extends to its passages.
2. **Econ serves them**, at its own routes (`/api/atlas/health`, `catalogue`, `ask`, `search`, `chunk/{id}`) over its own
   index, with its own prompts. No request names a knowledge base, so nothing the Econ page sends reaches the atlas, and
   tests there check both ways. The two share one Render service, its rate limit and its US$2.00 daily budget (A37,
   decision 3). They are apart in what they search, say, log and look like, not by access control: both Pages sites
   share an origin and the API is public. A second Render service from the same code would separate them fully.
3. **The checks carried over, plus the numbers rule.** The model cites sentences by number and code copies them; the
   check verifies every quote, and the atlas's numbers rule becomes a check: every number a claim states must be in
   the sentences it cites. Observation ids named in a question (or sent from "Ask about this observation") pin that
   observation's statement, what Stage 3 found and the Stage 3 pages that tested it, and its key figures first.
4. **The page** (`#/ask`, `evidence/js/chat.js`) ports the Econ page's behaviour (the stream, drafts, the cited runs,
   the claims, the evidence trail, Copy, the JSON export `atlas-chat-export/1`) but is built from the atlas's own
   components: its shell, page head and steps; passages as atlas cards in the observation, explainer or limit colours
   with their strength badge, lens chip and Stage 3 outcome; cited prose in the atlas's teal; a claim's several
   sentences in the categorical palette with a number each. Server text reaches the page only as text or through the
   ported renderer, which escapes first. The conversation survives a visit to a cited page and a reload (this tab).
5. **One address.** The API's address is `chat.api` in `content/site.yaml`; the Content Security Policy's `connect-src`
   names the same host and nothing else changes in it (a test checks they agree). For a local check, `?api=` accepts a
   same-origin path only.
6. **Which version the chat reads.** Econ's index records the passages' hash. The page compares it with its own
   `passages.meta.json` (the passages' hash, not `atlas.json`'s, since a change elsewhere in `atlas.json` such as this
   page's own settings changes no passage) and, if they differ, says the chat reads the atlas as at its date.
7. **New glossary terms** for the chat (passage, pinned passage, numbers check) are in `GLOSSARY.md` only: the page uses
   no `[[term]]` markup, and adding them to `content/glossary.yaml` would change the passages and so the index.

**Measured** (Econ, `reports/retrieval-atlas-v1.md`, free; delegated there under its D-013): with pinning, every lookup
(20 of 20) and every by-id need (5 of 5) in its test set reaches its gold pages among the 20 passages; context notes
are written but not indexed, and a page may give at most 2 passages, for the breadth of exploratory answers.

**The smoke test** (Econ D-039, `reports/atlas-chat-smoke-v1.md`; US$1.04 of the owner's US$2.00, after the
environment's OpenAI key was replaced, A38): 20 needs end to end; in the final state every answer passes the check (18
first time), every lookup and by-id answer cites its gold observation, and none states an association as a cause.
Reading the first run's answers found two figures in a list cited nowhere, so the numbers check now also refuses a
number in uncited prose, and atlas-answer-v2 asks each list item to cite its own sentences. The page's browser check
runs on one of the recorded answers. Then, at the owner's direction (clear language over exact wording for readers who are not technical; the numbers
check kept), atlas-answer-v3 answers in plain English (Econ D-040, `reports/atlas-chat-plain-v3.md`): 19 of 20 pass
first time, 41% shorter, a fifth of the analysts' terms; the page now says the answer rephrases the pages and the
quoted sentences are what it rests on. The owner adopted the prompts and the publishing (A39).

**Refreshing the chat.** After `atlas.build`, run `node analysis/atlas/passages.mjs` (a test fails otherwise). To make a
change reach the chat, in Econ: `econ atlas-ingest --ref <this repository's commit>`, set that sha in
`config/atlas.yaml`, `econ index --kb atlas`, commit and merge (Econ's `docs/deploy.md`).
