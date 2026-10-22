import pytest

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
    assert response.get_json() == {
        "service": "bookmarks-demo",
        "version": "1.0.0",
    }


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
