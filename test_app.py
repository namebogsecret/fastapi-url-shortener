import os, tempfile, importlib
import app as appmod
from fastapi.testclient import TestClient


def test_shorten_and_redirect(tmp_path, monkeypatch):
    # isolate the DB per test run
    monkeypatch.setattr(appmod, "DB", tmp_path / "t.db")
    appmod.init_db()
    client = TestClient(appmod.app)

    r = client.post("/shorten", json={"url": "https://example.com/page"})
    assert r.status_code == 200
    code = r.json()["code"]

    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code in (307, 302)
    assert r2.headers["location"] == "https://example.com/page"

    assert client.get(f"/stats/{code}").json()["hits"] == 1


def test_base62_roundtrip():
    for n in (0, 1, 61, 62, 12345):
        assert appmod.decode(appmod.encode(n)) == n
