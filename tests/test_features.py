from fastapi.testclient import TestClient
import src.storage as storage
from src.main import app

client = TestClient(app)


def setup_function():
    storage.features.clear()
    storage.environments.clear()
    storage.users.clear()
    storage.next_user_id = 1


def test_create_feature():
    response = client.post("/api/features", json={
        "key": "new-dashboard",
        "name": "Nouveau dashboard",
        "description": "Nouvelle interface"
    })
    assert response.status_code == 201
    assert response.json()["key"] == "new-dashboard"
    assert response.json()["enabled"] is False


def test_create_feature_duplicate():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    assert response.status_code == 409


def test_get_features():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.get("/api/features")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_feature():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.get("/api/features/new-dashboard")
    assert response.status_code == 200
    assert response.json()["key"] == "new-dashboard"


def test_get_feature_not_found():
    response = client.get("/api/features/unknown")
    assert response.status_code == 404


def test_update_feature():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.patch("/api/features/new-dashboard", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


def test_delete_feature():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.delete("/api/features/new-dashboard")
    assert response.status_code == 204


def test_enable_feature():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.patch("/api/features/new-dashboard/enable")
    assert response.status_code == 200
    assert response.json()["enabled"] is True


def test_disable_feature():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    client.patch("/api/features/new-dashboard/enable")
    response = client.patch("/api/features/new-dashboard/disable")
    assert response.status_code == 200
    assert response.json()["enabled"] is False


def test_set_env_config():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    client.post("/api/environments", json={"name": "prod"})
    response = client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True,
        "rollout": 25,
        "allowedGroups": ["beta-testers"],
        "allowedUsers": [1, 4, 8]
    })
    assert response.status_code == 200


def test_get_env_config():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    client.post("/api/environments", json={"name": "prod"})
    client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True,
        "rollout": 25
    })
    response = client.get("/api/features/new-dashboard/environments/prod/config")
    assert response.status_code == 200
    assert response.json()["rollout"] == 25


def test_delete_env_config():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    client.post("/api/environments", json={"name": "prod"})
    client.put("/api/features/new-dashboard/environments/prod/config", json={
        "enabled": True
    })
    response = client.delete("/api/features/new-dashboard/environments/prod/config")
    assert response.status_code == 204

def test_update_feature_not_found():
    response = client.patch("/api/features/unknown", json={"name": "Ghost"})
    assert response.status_code == 404

def test_delete_feature_not_found():
    response = client.delete("/api/features/unknown")
    assert response.status_code == 404

def test_enable_feature_not_found():
    response = client.patch("/api/features/unknown/enable")
    assert response.status_code == 404

def test_disable_feature_not_found():
    response = client.patch("/api/features/unknown/disable")
    assert response.status_code == 404

def test_set_env_config_feature_not_found():
    client.post("/api/environments", json={"name": "prod"})
    response = client.put("/api/features/unknown/environments/prod/config", json={"enabled": True})
    assert response.status_code == 404

def test_set_env_config_env_not_found():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.put("/api/features/new-dashboard/environments/unknown/config", json={"enabled": True})
    assert response.status_code == 404

def test_get_env_config_not_found():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.get("/api/features/new-dashboard/environments/prod/config")
    assert response.status_code == 404

def test_get_env_config_feature_not_found():
    response = client.get("/api/features/unknown/environments/prod/config")
    assert response.status_code == 404

def test_delete_env_config_not_found():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.delete("/api/features/new-dashboard/environments/prod/config")
    assert response.status_code == 404

def test_delete_env_config_feature_not_found():
    response = client.delete("/api/features/unknown/environments/prod/config")
    assert response.status_code == 404

def test_update_feature_description_only():
    client.post("/api/features", json={"key": "new-dashboard", "name": "Dashboard"})
    response = client.patch("/api/features/new-dashboard", json={"description": "Updated"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"