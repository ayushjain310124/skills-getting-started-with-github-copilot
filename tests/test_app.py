from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_user@example.com"

    # ensure clean start: remove test email if present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    result = resp.json()
    assert "Signed up" in result.get("message", "")

    # verify via GET that participant appears
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    data = resp2.json()
    assert email in data[activity]["participants"]

    # unregister
    resp3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp3.status_code == 200
    result3 = resp3.json()
    assert "Unregistered" in result3.get("message", "")

    # verify removal
    resp4 = client.get("/activities")
    data2 = resp4.json()
    assert email not in data2[activity]["participants"]


def test_double_signup_fails():
    activity = "Programming Class"
    email = "double_test@example.com"

    # ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # first signup ok
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # second signup should fail (already signed up)
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")
