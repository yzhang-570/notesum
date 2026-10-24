import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

import app as app_module

client = TestClient(app_module.app)


# Test 1: the health endpoint answers
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Test 2: summarize returns the mocked model reply
def test_summarize_with_mocked_model(monkeypatch):
    fake_reply = '{"summary": "Short summary", "action_items": ["Do thing"]}'
    monkeypatch.setattr(app_module, "call_model", lambda prompt: fake_reply)

    response = client.post("/summarize", json={"note": "Meeting notes here"})

    assert response.status_code == 200
    assert response.json()["summary"] == "Short summary"
    assert response.json()["action_items"] == ["Do thing"]
