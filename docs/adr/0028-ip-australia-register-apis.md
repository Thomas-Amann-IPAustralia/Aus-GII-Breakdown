# 0028: IP Australia's register APIs: a client, a corpus source, and IP RAPID checked against the register

**Date:** 2026-10-27. **Whose:** the owner obtained the access and asked for the code and the check; Claude decided how.
Adopting any finding as a conclusion, and changing the lenses with it, is the owner's decision.

**Context.** The owner obtained client credentials for IP Australia's Trade Mark, Patent and Design Search APIs (test
and production; contracts in `docs/ip-reg-api/`) and asked for code to query them in future, then for the access to be
used to fill the dataset's gaps and to check whether IP RAPID is accurate.

**Decision.**

1. **A client in the corpus package** (`src/corpus/ipa_api.py`, with a command line): OAuth client credentials from
   the environment (`IPA_API_*_DEV` is production, `IPA_API_*_TEST` the test host), pacing at 540 calls a minute per
   API across threads (the limit is 600), retries for production's patent API (about half its calls answer 403 or 500
   at random), date searches split until each part is under the 10,000-number cap, and a record that keeps failing
   marked rather than fatal. Tests use a fake server (`tests/test_ipa_api.py`).
2. **A corpus source, `ipa_api`**, so the harvest is recorded and repeatable: every trade mark and design number the
   searches find (`numbers`, repo), and records fetched for named targets (a random sample of each right, and IP
   RAPID's gaps), flattened without names (`trade_marks`, `designs`, `patents`, repo) and with owners' names
   (`owners`, R2). The raw responses go to R2, as `iprapid/party` does, because they name individuals. Patents cannot
   be listed (the search ignores fields), so they are sampled from IP RAPID. A run takes about two hours and resumes
   the same day.
3. **The check is an audit, kept apart from the lenses** (`analysis/audit/api_check.py`, writing to
   `analysis/audit/output/api/`; observations V1 to V14 in `docs/audit-ipa-api.md`). Records the register changed after
   the release are left out of the field comparison. Two differences are recorded as definitions, not errors: a Madrid
   trade mark's IP RAPID date is the register's IR notification date, and a PCT patent's is its national phase entry.
4. **Findings.** IP RAPID is complete to within the week since its release (V2, V3) and its fields agree with the
   register's in 99.7% to 100% of a random sample of every right (V5 to V9). Its gaps are in publication: the register
   holds an ABN or ACN for 83.8% of the OQ7 marks (V12), a country for 61.4% of the OQ14 designs, which reproduces
   IP Australia's resident design counts (V13), and an "Examination expedited" event on every priority-claiming mark
   since FY2020, which IP RAPID does not publish (V14, OQ6). Trade mark numbers 1,978,060 to 1,980,352 were not used
   (V10); the register does not explain the IP Report 2019's 2018 count (V11).
5. **No lens or observation changes yet.** Attaching the fills to `rights` would change U45 (ABN linking), U7 and
   U13's design shares and U34's expedite series; that and rewording the request to IP Australia are for the owner
   (OQ15, OQ16).

**Consequences.** `uv run corpus run ipa_api` then `uv run python -m audit.api_check --live` repeat the check against
any later release. The `ipa_api` tables can be joined to `rights` by right type and application number when the owner
decides. The test environment is for trying requests only: it is an old, partial copy.
