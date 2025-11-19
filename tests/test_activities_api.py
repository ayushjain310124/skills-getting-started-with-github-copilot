import os
import sys
import uuid
from urllib.parse import quote
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_smoke_and_environment():
    """Diagnostic smoke test to help with test collection/runtime issues.

    Prints environment details so CI or the agent runner can show why tests
    may not be discovered or executed.
    """
    print("CWD:", os.getcwd())
    print("PYTHON:", sys.executable)
    print("sys.path:", sys.path)
    root = Path(".").resolve()
    print("Repository root files:")
    for p in sorted([str(p.relative_to(root)) for p in root.glob("**/*") if p.is_file()][:50]):
        print(" -", p)

    # Basic assertion to ensure pytest runs tests from this file
    assert True


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Known activity should exist
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    quoted = quote(activity, safe="")
    # unique email to avoid colliding with existing participants
    email = f"tester+{uuid.uuid4().hex}@example.com"

    # fetch initial count
    before = len(client.get("/activities").json()[activity]["participants"])

    # signup
    resp = client.post(f"/activities/{quoted}/signup", params={"email": email})
    assert resp.status_code == 200, resp.text
    assert "Signed up" in resp.json().get("message", "")

    # verify participant was added
    after = len(client.get("/activities").json()[activity]["participants"])
    assert after == before + 1

    # attempting to sign up again returns 400
    resp2 = client.post(f"/activities/{quoted}/signup", params={"email": email})
    assert resp2.status_code == 400

    # unregister
    resp3 = client.post(f"/activities/{quoted}/unregister", params={"email": email})
    assert resp3.status_code == 200, resp3.text
    assert "Unregistered" in resp3.json().get("message", "")

    # verify removed
    final = len(client.get("/activities").json()[activity]["participants"])
    assert final == before


def test_unregister_nonexistent_returns_400():
    activity = "Chess Club"
    quoted = quote(activity, safe="")
    email = f"noone+{uuid.uuid4().hex}@example.com"

    resp = client.post(f"/activities/{quoted}/unregister", params={"email": email})
    assert resp.status_code == 400
