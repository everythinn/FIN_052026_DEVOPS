from fastapi.testclient import TestClient
import src.storage as storage
from src.main import app

client = TestClient(app)

def setup_function():
    storage.environments.clear()

def test_create_environment():
    response = client.post("/api/environments", json={
        "name": "prod",
        "description": "Production"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "prod"

def test_create_environment_duplicate():
    client.post("/api/environments", json={"name": "prod", "description": "Production"})
    response = client.post("/api/environments", json={"name": "prod", "description": "Production"})
    assert response.status_code == 409

def test_get_environments():
    client.post("/api/environments", json={"name": "prod", "description": "Production"})
    response = client.get("/api/environments")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_environment():
    client.post("/api/environments", json={"name": "prod", "description": "Production"})
    response = client.get("/api/environments/prod")
    assert response.status_code == 200
    assert response.json()["name"] == "prod"

def test_get_environment_not_found():
    response = client.get("/api/environments/unknown")
    assert response.status_code == 404

def test_update_environment():
    client.post("/api/environments", json={"name": "prod", "description": "Production"})
    response = client.patch("/api/environments/prod", json={"description": "Updated"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"

def test_delete_environment():
    client.post("/api/environments", json={"name": "prod", "description": "Production"})
    response = client.delete("/api/environments/prod")
    assert response.status_code == 204

def test_delete_environment_not_found():
    response = client.delete("/api/environments/unknown")
    assert response.status_code == 404

def test_update_environment_not_found():
    response = client.patch("/api/environments/unknown", json={"description": "Ghost"})
    assert response.status_code == 404