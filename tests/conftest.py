import pytest

import fetch


class FakeResponse:
    """Stands in for an httpx.Response. fetch.py only calls .json()."""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture
def alma(monkeypatch):
    """A fake Alma API that never touches the network.

    Returns an empty dict. A test fills it with {exact URL: JSON payload}.
    Requesting any URL not in the dict fails the test, so a wrong page
    offset, record ID or API key is caught. (pytest.fail is used rather than
    a KeyError because fetch.py catches KeyError and would hide the mistake.)
    The fake also requires a ``timeout`` argument, like every real request
    in fetch.py has.

    The API keys are set to test values so URLs in tests are predictable
    and real keys from a local .env never appear in test output.
    """
    monkeypatch.setattr(fetch, "apikey1", "test-nz-key")
    monkeypatch.setattr(fetch, "apikey2", "test-bibs-key")
    responses = {}

    def fake_get(url, timeout):
        if url not in responses:
            pytest.fail(f"unexpected request to {url}")
        return FakeResponse(responses[url])

    monkeypatch.setattr(fetch.httpx, "get", fake_get)
    return responses
