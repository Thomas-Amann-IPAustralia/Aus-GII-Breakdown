"""The client for IP Australia's register APIs (src/corpus/ipa_api.py, ADR 0028), against a fake server."""

import pytest

from corpus import ipa_api
from corpus.core import CorpusError


class FakeResponse:
    def __init__(self, status, body=None, headers=None):
        self.status_code, self._body, self.headers = status, body or {}, headers or {}
        self.text = str(self._body)

    def json(self):
        return self._body


class FakeSession:
    """Answers the token endpoint, then each call from a queue of (status, body); records what was asked."""

    def __init__(self, answers):
        self.answers, self.asked, self.headers, self.tokens = list(answers), [], {}, 0

    def post(self, url, data=None, timeout=None):
        assert url.endswith(ipa_api.TOKEN_PATH) and data["grant_type"] == "client_credentials"
        self.tokens += 1
        return FakeResponse(200, {"access_token": f"t{self.tokens}", "expires_in": 86400})

    def request(self, method, url, json=None, headers=None, timeout=None):
        self.asked.append((method, url, json, headers["Authorization"]))
        return FakeResponse(*self.answers.pop(0))


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("IPA_API_ID_DEV", "id")
    monkeypatch.setenv("IPA_API_SEC_DEV", "secret")
    monkeypatch.setattr(ipa_api.time, "sleep", lambda s: None)
    c = ipa_api.Client("prod")

    def use(answers):
        c.session = FakeSession(answers)
        return c

    return use


def test_credentials_come_from_the_environment(monkeypatch):
    for v in ("IPA_API_ID_PROD", "IPA_API_SEC_PROD", "IPA_API_ID_DEV", "IPA_API_SEC_DEV"):
        monkeypatch.delenv(v, raising=False)
    with pytest.raises(CorpusError, match="IPA_API_ID_PROD"):
        ipa_api.credentials("prod")
    monkeypatch.setenv("IPA_API_ID_DEV", "a")
    monkeypatch.setenv("IPA_API_SEC_DEV", "b")
    assert ipa_api.credentials("prod") == ("a", "b")


def test_a_record_is_fetched_by_number_and_a_missing_one_is_none(client):
    c = client([(200, {"number": "1000000"}), (404, {"error": "not found"})])
    assert c.get("trade_mark", 1000000) == {"number": "1000000"}
    assert c.get("design", "202010001") is None
    (m1, u1, _, auth), (_, u2, _, _) = c.session.asked
    assert m1 == "GET" and u1.endswith("/australian-trade-mark-search-api/v1/trade-mark/1000000")
    assert u2.endswith("/australian-design-search-api/v1/design/202010001") and auth == "Bearer t1"


def test_production_patents_random_invalid_client_is_retried(client):
    c = client([(403, {"error": "Invalid Client"})] * 3 + [(200, {"ipRightStatusCode": "GRANTED"})])
    assert c.get("patent", "2019100001")["ipRightStatusCode"] == "GRANTED"
    assert c.retries == 3 and c.calls == 4


def test_a_record_that_keeps_failing_is_marked_not_fatal(client):
    c = client([(500, {})] * 8 + [(200, {"number": "2"})])
    got = dict(c.get_many("trade_mark", [1, 2], workers=1))
    assert ipa_api.failed(got["1"]) and got["2"] == {"number": "2"} and not ipa_api.failed(None)


def test_an_expired_token_is_renewed_and_other_errors_raise(client):
    c = client([(401, {}), (200, {"ok": 1}), (400, {"error": "bad request"})])
    assert c.get("design", "1") == {"ok": 1}
    assert c.session.asked[1][3] == "Bearer t2"
    with pytest.raises(CorpusError, match="400"):
        c.get("design", "2")


def test_ids_halves_a_date_range_until_every_number_is_returned(client):
    def answer(n_found, count):
        return (200, {"count": count, "trademarkIds": [str(i) for i in range(n_found)]})

    c = client([answer(2, 5), answer(3, 3), answer(2, 2)])  # whole range capped; each half complete
    got = c.ids("trade_mark", "LODGEMENT_DATE", "2018-01-01", "2018-01-10")
    assert got == ["0", "1", "2", "0", "1"]
    halves = [a[2]["rows"][-1]["query"]["date"] for a in c.session.asked[1:]]
    assert halves == [
        {"type": "LODGEMENT_DATE", "from": "2018-01-01", "to": "2018-01-05"},
        {"type": "LODGEMENT_DATE", "from": "2018-01-06", "to": "2018-01-10"},
    ]


def test_ids_splits_a_search_the_server_keeps_failing(client):
    c = client(
        [(500, {})] * 8 + [(200, {"count": 1, "designNumbers": ["a"]}), (200, {"count": 1, "designNumbers": ["b"]})]
    )
    assert c.ids("design", "FILED", "2020-01-01", "2020-01-02") == ["a", "b"]


def test_pace_keeps_under_the_limit(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(ipa_api.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(ipa_api.time, "sleep", lambda s: clock.__setitem__(0, clock[0] + s))
    pace = ipa_api._Pace(3)
    for _ in range(4):
        pace.wait()
    assert clock[0] >= 60  # the fourth call waited for the first to leave the window
