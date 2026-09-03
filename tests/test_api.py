"""The HTTP API as seen by the browser."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Language Detector" in response.text


def test_list_languages() -> None:
    response = client.get("/api/languages")
    assert response.status_code == 200
    codes = {item["code"] for item in response.json()}
    assert "fr" in codes
    assert "en" in codes


def test_detect_post() -> None:
    response = client.post(
        "/api/detect",
        json={
            "text": "Bonjour, je voudrais un café et une tartine s'il vous plaît.",
            "n": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "fr"
    assert data["n"] == 3
    assert data["top_ngrams"]
    assert data["scores"][0]["code"] == "fr"


def test_text_without_letters() -> None:
    response = client.post("/api/detect", json={"text": "2024 !!!", "n": 3})
    assert response.status_code == 400
