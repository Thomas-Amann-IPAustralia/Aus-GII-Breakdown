# IP Australia's register APIs

IP Australia's Trade Mark, Patent and Design Search APIs answer from the live register: the records its search sites
show. IP RAPID is a weekly extract of the same register. The contracts are in this folder (`tm-api.json`,
`patent-api.json`, `design-api.json`; the `*-exchange-api.json` files are their Exchange metadata). The client is
`src/corpus/ipa_api.py`; what it was used for is in ADR 0028 and `docs/audit-ipa-api.md`.

## Access

OAuth 2.0 client credentials, from IP Australia's API portal. The client reads them from the environment:

| Environment | Host | Variables |
|---|---|---|
| `prod` (the default) | `production.api.ipaustralia.gov.au` | `IPA_API_ID_DEV`, `IPA_API_SEC_DEV` (or `IPA_API_ID_PROD`, `IPA_API_SEC_PROD`) |
| `test` | `test.api.ipaustralia.gov.au` | `IPA_API_ID_TEST`, `IPA_API_SEC_TEST` |

The pair named `DEV` is production's: it is refused by the test host, and the `TEST` pair by production. Test holds an
old, partial copy of the register (some designs filed in 2020 are missing; its patent search finds 2,069,356
patents), so use it to try requests, not as evidence. Tokens last a day; the client renews them.

## From the command line

```sh
uv run python -m corpus.ipa_api get trade_mark 1000000             # one record, as JSON
uv run python -m corpus.ipa_api get patent 2019100001
uv run python -m corpus.ipa_api get design 202310001
uv run python -m corpus.ipa_api count trade_mark LODGEMENT_DATE 2018-01-01 2018-12-31
uv run python -m corpus.ipa_api ids design FILED 2023-01-01 2023-01-31  # every number, one a line
uv run python -m corpus.ipa_api search trade_mark '{"rows": [{"query": {"acnArbnAbn": "15101088626"}}]}'
uv run python -m corpus.ipa_api --env test get patent 2019100001
```

## From Python

```python
from corpus.ipa_api import Client

c = Client()                                       # production
c.get("trade_mark", 1000000)                       # dict, or None if there is no such record
dict(c.get_many("design", ["202310001", "202310002"]))   # in parallel, paced
c.count("trade_mark", [{"query": {"flags": ["INTERNATIONAL_REGISTRATION"],
                                  "date": {"type": "LODGEMENT_DATE", "from": "2018-01-01", "to": "2018-12-31"}}}])
c.ids("trade_mark", "LODGEMENT_DATE", "2018-01-01", "2018-12-31")          # 78,643 numbers
c.ids("design", "FILED", "1900-01-01", "2026-12-31", changedSinceDate="2026-10-19")   # changed since a date
list(c.page_all("trade_mark", {"rows": [{"query": {"trademarkNumber": "1000000"}}]}))  # whole records, 100 a call
```

The search bodies are the contracts' `TrademarkApiAdvancedSearchRequest` and `DesignApiAdvancedSearchRequest`: rows of
conditions (dates by type, owner, ABN or ACN, class, status, flags such as `INTERNATIONAL_REGISTRATION`), joined by
`AND`, `OR` or `AND_NOT`.

## What to know (found on 27 October 2026)

- **Rate limit:** 600 requests a minute for each API (`x-ratelimit-*` headers; the reset is in milliseconds). The
  client stays at 540 a minute across threads and waits out a 429. A whole record takes about a second, so about 10
  requests at once reach the limit.
- **Production's patent API fails about half its calls at random**, with 403 `{"error": "Invalid Client"}` or 500,
  with a good token; the same call succeeds when repeated. The client retries production's patent calls up to 24
  times. A call that still fails comes back from `get_many` as `{"_error": ...}` (`ipa_api.failed`), not an
  exception.
- **Searches return at most 10,000 numbers** (`count` is the true total). `ids` halves the date range until each
  part fits. Several big searches at once make the trade mark search answer 500 for minutes: `ids` splits a search
  that keeps failing, but send searches two or three at a time.
- **The patent search cannot list patents.** It ignores field syntax (a date query finds every patent) and returns at
  most 5,000 numbers. Patents are fetched by number.
- **Dates differ from IP RAPID's by design in two places.** A Madrid trade mark's `lodgementDate` is the international
  registration's date; IP RAPID's application date is the register's `irNotificationDate` (when IP Australia was
  notified), often the next year. A PCT patent's `filedDate` is the international filing date; IP RAPID's application
  date is `pctNationalPhaseEntryDate` (in `bibliographicData.pctDetails`).
- **Not in the APIs:** plant breeder's rights. **In them but not in IP RAPID:** patents' inventors, owners' street
  addresses and ACNs, the trade mark register's full event history, and goods and services text.
- **Personal information:** records name individuals and give their addresses. Keep raw responses out of the
  repository (the corpus keeps them in R2, as it keeps IP RAPID's `party`).
