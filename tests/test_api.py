import os
import sys
import importlib
from fastapi.testclient import TestClient

# Ensure `src` is on sys.path so we can import the app module
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import app as app_module


def client_with_fresh_state():
    importlib.reload(app_module)
    return TestClient(app_module.app)


def test_get_activities():
    client = client_with_fresh_state()
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Soccer Team" in data


def test_signup_and_remove_participant():
    client = client_with_fresh_state()
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # signup
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # remove
    r2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r2.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_duplicate_signup_returns_400():
    client = client_with_fresh_state()
    activity = "Soccer Team"
    email = "duplicate@example.com"
    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400
