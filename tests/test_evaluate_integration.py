from fastapi.testclient import TestClient
import src.storage as storage
from src.main import app

client = TestClient(app)


def setup_function():
    storage.features.clear()
    storage.environments.clear()
    storage.users.clear()
    storage.groups.clear()
    storage.next_user_id = 1
    storage.next_group_id = 1


def setup_base():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    client.post("/api/environments", json={"name": "prod"})
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    client.patch("/api/features/new-dashboard/enable")
    client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True,
        "rollout": 0,
        "allowedUsers": [],
        "allowedGroups": []
    })


def test_evaluate_user_explicitly_allowed():
    setup_base()
    client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True,
        "rollout": 0,
        "allowedUsers": [1],
        "allowedGroups": []
    })
    response = client.get("/api/features/new-dashboard/evaluate?userId=1&env=prod")
    assert response.status_code == 200
    assert response.json()["enabled"] is True
    assert response.json()["reason"] == "user explicitly allowed"


def test_evaluate_user_in_group():
    setup_base()
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/groups/1/users/1")
    client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True,
        "rollout": 0,
        "allowedUsers": [],
        "allowedGroups": ["beta-testers"]
    })
    response = client.get("/api/features/new-dashboard/evaluate?userId=1&env=prod")
    assert response.status_code == 200
    assert response.json()["enabled"] is True
    assert "beta-testers" in response.json()["reason"]


def test_evaluate_feature_disabled():
    setup_base()
    client.patch("/api/features/new-dashboard/disable")
    response = client.get("/api/features/new-dashboard/evaluate?userId=1&env=prod")
    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["reason"] == "feature is disabled globally"


def test_evaluate_feature_not_found():
    response = client.get("/api/features/unknown/evaluate?userId=1&env=prod")
    assert response.status_code == 404


def test_evaluate_user_not_found():
    setup_base()
    response = client.get("/api/features/new-dashboard/evaluate?userId=999&env=prod")
    assert response.status_code == 404