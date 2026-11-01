import pytest
from pathlib import Path

from app.main import create_app, reset_store


@pytest.fixture
def client():
    reset_store()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"Keep the good links close." in response.data


def test_info(client, monkeypatch):
    monkeypatch.setenv("APP_COMMIT", "abcdef012345")
    response = client.get("/info")
    assert response.status_code == 200
    assert response.get_json() == {
        "service": "bookmarks-demo",
        "version": "1.0.0",
        "commit": "abcdef0",
    }


def test_info_defaults_to_local(client, monkeypatch):
    monkeypatch.delenv("APP_COMMIT", raising=False)
    assert client.get("/info").get_json()["commit"] == "local"


def test_security_headers(client):
    expected = {
        "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "X-Frame-Options": "DENY",
    }
    for path in ("/", "/health"):
        response = client.get(path)
        for header, value in expected.items():
            assert response.headers[header] == value


def test_app_js_does_not_use_inner_html():
    app_js = Path(__file__).parent.parent / "app" / "static" / "app.js"
    assert "innerHTML" not in app_js.read_text(encoding="utf-8")


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_valid(client):
    response = client.post(
        "/bookmarks",
        json={"title": "Example", "url": "https://example.com"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 1
    assert body["title"] == "Example"
    assert body["url"] == "https://example.com"


def test_create_missing_title(client):
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_bad_url(client):
    response = client.post(
        "/bookmarks",
        json={"title": "Example", "url": "ftp://example.com"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_list_bookmarks(client):
    client.post(
        "/bookmarks",
        json={"title": "Example", "url": "https://example.com"},
    )
    response = client.get("/bookmarks")
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["title"] == "Example"


def test_delete_existing(client):
    created = client.post(
        "/bookmarks",
        json={"title": "Example", "url": "https://example.com"},
    ).get_json()
    response = client.delete(f"/bookmarks/{created['id']}")
    assert response.status_code == 204


def test_delete_missing(client):
    response = client.delete("/bookmarks/999")
    assert response.status_code == 404
