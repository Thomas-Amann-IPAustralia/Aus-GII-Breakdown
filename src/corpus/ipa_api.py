"""IP Australia's register APIs: the live trade mark, patent and design records, by number or by search.

    uv run python -m corpus.ipa_api get trade_mark 1000000          # one record, as JSON
    uv run python -m corpus.ipa_api get patent 2019100001 --env test
    uv run python -m corpus.ipa_api count trade_mark LODGEMENT_DATE 2018-01-01 2018-12-31
    uv run python -m corpus.ipa_api ids design FILED 2023-01-01 2023-01-31

The three APIs (the Australian Trade Mark, Patent and Design Search APIs; their contracts are in `docs/ip-reg-api/`)
are what IP Australia's search sites run on, so they answer from the register as it is now, where IP RAPID is a
weekly extract of it. Access is OAuth 2.0 client credentials, a token a day, from IP Australia's API portal; the
client id and secret come from the environment:

- `prod` (production.api.ipaustralia.gov.au): `IPA_API_ID_DEV` and `IPA_API_SEC_DEV` (or `IPA_API_ID_PROD` and
  `IPA_API_SEC_PROD`). The default.
- `test` (test.api.ipaustralia.gov.au): `IPA_API_ID_TEST` and `IPA_API_SEC_TEST`. Its data is an old, partial copy
  of the register (some designs filed in 2020 are missing), so use it to try requests, not for evidence.

What the client handles, as found on 27 October 2026 (ADR 0028):

- The limit is 600 requests a minute for each API (headers `x-ratelimit-*`; the reset is in milliseconds). The
  client paces itself below it, across threads, and waits out a 429.
- About half of production's patent requests answer 403 `{"error": "Invalid Client"}` or 500 at random, with a good
  token: the same request answers 200 when sent again. Those answers carry no rate-limit headers and do not count
  toward the limit, so the client retries them at once (up to 24 times) without counting them; other 5xx are
  retried with backoff. With 24 threads, production served about 630 patents a minute this way.
- Searches return at most 10,000 numbers each (`count` is the true total); `ids` splits a date range until each
  part fits. Big searches sent several at a time can answer 500 for minutes; `ids` splits those too, so send
  searches two or three at a time. `page` (trade marks and designs) returns up to 100 whole records a call.
- A record that does not exist answers 404, returned here as `None`. Records are returned as the API sends them:
  they include individuals' names and addresses, so keep raw responses out of the repo (as `party` is kept in R2).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import threading
import time
from collections import deque
from collections.abc import Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor

import requests

from .core import UA, CorpusError

ENVS = {
    "prod": ("https://production.api.ipaustralia.gov.au", ("PROD", "DEV")),
    "test": ("https://test.api.ipaustralia.gov.au", ("TEST",)),
}
TOKEN_PATH = "/public/external-token-api/v1/access_token"
APIS = {  # right -> (base path, record path, field holding a search's numbers)
    "trade_mark": ("/public/australian-trade-mark-search-api/v1", "trade-mark", "trademarkIds"),
    "patent": ("/public/australian-patent-search-api/v1", "patent", "results"),
    "design": ("/public/australian-design-search-api/v1", "design", "designNumbers"),
}
PER_MINUTE = 540  # each API allows 600; stay under it
SEARCH_CAP = 10_000  # numbers a search returns at most
RETRY = (403, 429, 500, 502, 503, 504)


def credentials(env: str) -> tuple[str, str]:
    """The client id and secret for an environment, from the first pair of variables that is set."""
    for suffix in ENVS[env][1]:
        cid, sec = os.environ.get(f"IPA_API_ID_{suffix}"), os.environ.get(f"IPA_API_SEC_{suffix}")
        if cid and sec:
            return cid, sec
    names = " or ".join(f"IPA_API_ID_{s} and IPA_API_SEC_{s}" for s in ENVS[env][1])
    raise CorpusError(f"no credentials for IP Australia's {env} APIs: set {names}")


class _Pace:
    """At most `n` calls in any 60 seconds, shared by threads."""

    def __init__(self, n: int):
        self.n, self.calls, self.lock = n, deque(), threading.Lock()

    def wait(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                while self.calls and now - self.calls[0] >= 60:
                    self.calls.popleft()
                if len(self.calls) < self.n:
                    self.calls.append(now)
                    return
                pause = 60 - (now - self.calls[0])
            time.sleep(max(pause, 0.05))

    def refund(self) -> None:
        """Give back the last call: the server did not count it."""
        with self.lock:
            if self.calls:
                self.calls.pop()


class Client:
    """A session with one environment's APIs. Thread-safe: `get_many` and `page_all` run calls in parallel."""

    def __init__(self, env: str = "prod", *, per_minute: int = PER_MINUTE, tries: int = 8, timeout: int = 120):
        if env not in ENVS:
            raise CorpusError(f"unknown environment {env!r}: one of {', '.join(ENVS)}")
        self.env, self.host = env, ENVS[env][0]
        self.tries, self.timeout = tries, timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = UA
        adapter = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=64)  # many threads, one host
        self.session.mount("https://", adapter)
        self.pace = {right: _Pace(per_minute) for right in APIS}
        self._token, self._expires, self._lock = None, 0.0, threading.Lock()
        self.calls = 0  # sent, retries included
        self.retries = 0

    # -- plumbing -------------------------------------------------------------------------------------------------

    def token(self, *, renew: bool = False) -> str:
        with self._lock:
            if renew or not self._token or time.time() > self._expires - 300:
                cid, sec = credentials(self.env)
                r = self.session.post(
                    self.host + TOKEN_PATH,
                    data={"grant_type": "client_credentials", "client_id": cid, "client_secret": sec},
                    timeout=self.timeout,
                )
                if r.status_code != 200:
                    raise CorpusError(f"IP Australia's {self.env} token endpoint answered {r.status_code}: {r.text}")
                body = r.json()
                self._token, self._expires = body["access_token"], time.time() + float(body.get("expires_in", 3600))
            return self._token

    def request(self, right: str, method: str, path: str, body: dict | None = None) -> requests.Response | None:
        """One call to a right's API, paced and retried; `None` for a 404."""
        url = self.host + APIS[right][0] + path
        tries = self.tries * (3 if right == "patent" and self.env == "prod" else 1)  # half its calls fail at random
        for i in range(tries):
            self.pace[right].wait()
            self.calls += 1
            try:
                r = self.session.request(
                    method,
                    url,
                    json=body,
                    headers={"Authorization": f"Bearer {self.token()}", "Accept": "application/json"},
                    timeout=self.timeout,
                )
            except requests.RequestException as e:
                if i == tries - 1:
                    raise CorpusError(f"{method} {url} failed: {e}") from e
                r = None
            if r is not None:
                if r.status_code == 200:
                    return r
                if r.status_code == 404:
                    return None
                if r.status_code == 401:
                    self.token(renew=True)
                elif r.status_code not in RETRY:
                    raise CorpusError(f"{method} {url} answered {r.status_code}: {r.text[:300]}")
                if r.status_code == 429:
                    reset = r.headers.get("x-ratelimit-reset")
                    time.sleep(min(float(reset) / 1000, 60) if reset else 10)
                    continue
            self.retries += 1
            if r is not None and r.status_code in (403, 500) and "x-ratelimit-remaining" not in r.headers:
                # production patents' random failures carry no rate-limit headers: the limit did not count them, and
                # the next call usually succeeds, so retry at once
                self.pace[right].refund()
                time.sleep(0.05)
                continue
            time.sleep(min(0.5 * 2**i, 20))
        raise CorpusError(f"{method} {url} kept failing after {tries} tries (last: {r and r.status_code})")

    # -- records --------------------------------------------------------------------------------------------------

    def get(self, right: str, number: str | int) -> dict | None:
        """A right's record by its number (trade mark number, patent application number, design number)."""
        r = self.request(right, "GET", f"/{APIS[right][1]}/{number}")
        return None if r is None else r.json()

    def get_many(self, right: str, numbers: Iterable, *, workers: int = 8) -> Iterator[tuple[str, dict | None]]:
        """(number, record or None) for each number, fetched in parallel, in the order given. A record that still
        fails after every retry comes back as `{"_error": message}` (see `failed`), so one bad call does not stop a
        harvest."""

        def one(n):
            try:
                return self.get(right, n)
            except CorpusError as e:
                return {"_error": str(e)}

        numbers = [str(n) for n in numbers]
        with ThreadPoolExecutor(workers) as pool:
            yield from zip(numbers, pool.map(one, numbers), strict=True)

    # -- searches -------------------------------------------------------------------------------------------------

    def search(self, right: str, body: dict, *, quick: bool = False) -> dict:
        """POST /search/advanced (or /search/quick) with the contract's request body; the answer as sent."""
        return self.request(
            right, "POST", "/search/quick" if quick or right == "patent" else "/search/advanced", body
        ).json()

    def page(self, right: str, body: dict, number: int, size: int = 100) -> dict:
        """POST /page/advanced: one page of whole records (trade marks and designs)."""
        return self.request(right, "POST", "/page/advanced", {**body, "pageNumber": number, "pageSize": size}).json()

    def count(self, right: str, rows: list[dict], **body) -> dict:
        """The number of records an advanced search finds, and its aggregations (status and so on)."""
        out = self.search(right, {"rows": rows, **body})
        return {"count": out["count"], "aggregations": out.get("aggregations")}

    def ids(
        self,
        right: str,
        date_type: str,
        start: str | dt.date,
        end: str | dt.date,
        *,
        rows: list[dict] = (),
        **body,
    ) -> list[str]:
        """Every number an advanced search finds with a date of `date_type` from `start` to `end` (inclusive), the
        range halved until each part returns all its numbers. `rows` adds conditions (they are ANDed); `body` adds
        request fields (for example `changedSinceDate="2026-10-19"`)."""
        start, end = dt.date.fromisoformat(str(start)), dt.date.fromisoformat(str(end))
        date = {"op": "AND", "query": {"date": {"type": date_type, "from": str(start), "to": str(end)}}}
        try:
            out = self.search(right, {"rows": [*rows, date], **body})
        except CorpusError:
            if start == end:
                raise
            out = None  # a search that keeps answering 500 is usually one too big for the server: split it
        if out is not None:
            found = out[APIS[right][2]] or []
            if out["count"] <= len(found):
                return list(found)
            if start == end:
                raise CorpusError(f"{right} {date_type} {start}: {out['count']} records in one day, over the cap")
        mid = start + (end - start) // 2
        return self.ids(right, date_type, start, mid, rows=rows, **body) + self.ids(
            right, date_type, mid + dt.timedelta(days=1), end, rows=rows, **body
        )

    def page_all(self, right: str, body: dict, *, size: int = 100, workers: int = 4) -> Iterator[dict]:
        """Every record a search finds, a page at a time (keep each search under 10,000 records: page past the cap
        is not served)."""
        first = self.page(right, body, 0, size)
        key = "trademarks" if right == "trade_mark" else next(k for k, v in first.items() if isinstance(v, list))
        yield from first[key] or []
        pages = range(1, -(-min(first["count"], SEARCH_CAP) // size))
        with ThreadPoolExecutor(workers) as pool:
            for out in pool.map(lambda n: self.page(right, body, n, size), pages):
                yield from out[key] or []


def failed(record: dict | None) -> bool:
    """Whether `get_many` gave up on this record."""
    return isinstance(record, dict) and "_error" in record


# -- command line ---------------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m corpus.ipa_api", description=__doc__.split("\n\n")[0])
    p.add_argument("--env", choices=list(ENVS), default="prod")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", help="one record by number, as JSON")
    g.add_argument("right", choices=list(APIS))
    g.add_argument("number")
    for name, help_ in (("count", "how many records have a date in a range"), ("ids", "their numbers, one a line")):
        c = sub.add_parser(name, help=help_)
        c.add_argument("right", choices=["trade_mark", "design"])
        c.add_argument("date_type", help="for example LODGEMENT_DATE (trade marks) or FILED (designs)")
        c.add_argument("start")
        c.add_argument("end")
    s = sub.add_parser("search", help="POST a request body (JSON) to a right's search; prints the answer")
    s.add_argument("right", choices=list(APIS))
    s.add_argument("body")
    s.add_argument("--quick", action="store_true")
    a = p.parse_args(argv)
    client = Client(a.env)
    if a.cmd == "get":
        rec = client.get(a.right, a.number)
        if rec is None:
            print(f"{a.right} {a.number}: not found", file=sys.stderr)
            return 1
        print(json.dumps(rec, indent=2))
    elif a.cmd == "count":
        q = {"date": {"type": a.date_type, "from": a.start, "to": a.end}}
        print(json.dumps(client.count(a.right, [{"query": q}]), indent=2))
    elif a.cmd == "ids":
        print("\n".join(client.ids(a.right, a.date_type, a.start, a.end)))
    else:
        print(json.dumps(client.search(a.right, json.loads(a.body), quick=a.quick), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
