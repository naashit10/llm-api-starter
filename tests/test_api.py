import os

os.environ["LLM_PROVIDER"] = "fake"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

LONG_TEXT = "This is a long enough text for the validation rule."


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summarize_fake_mode():
    response = client.post("/summarize", json={"text": LONG_TEXT})
    assert response.status_code == 200
    assert response.json()["model"] == "fake"


def test_summarize_rejects_short_text():
    response = client.post("/summarize", json={"text": "short"})
    assert response.status_code == 422


def test_analyze_fake_mode():
    response = client.post("/analyze", json={"text": LONG_TEXT})
    assert response.status_code == 200
    assert response.json()["sentiment"] in ["positive", "neutral", "negative"]


def test_summarize_llm_failure(monkeypatch):
    def boom(text, max_words):
        raise RuntimeError("fake failure")

    monkeypatch.setattr("app.main.summarize_text", boom)

    response = client.post("/summarize", json={"text": LONG_TEXT})
    assert response.status_code == 502
    assert response.json()["detail"] == "The LLM call failed"