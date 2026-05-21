from fastapi.testclient import TestClient
import src.storage as storage
from src.main import app

client = TestClient(app)

def setup_function():
    storage.groups.clear()
    storage.next_group_id = 1
    storage.users.clear()
    storage.next_user_id = 1

def test_create_group():
    response = client.post("/api/groups", json={
        "name": "beta-testers",
        "description": "Utilisateurs bêta"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "beta-testers"
    assert response.json()["id"] == 1

def test_create_group_duplicate():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.post("/api/groups", json={"name": "beta-testers"})
    assert response.status_code == 409

def test_get_groups():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_group():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.get("/api/groups/1")
    assert response.status_code == 200
    assert response.json()["name"] == "beta-testers"

def test_get_group_not_found():
    response = client.get("/api/groups/999")
    assert response.status_code == 404

def test_update_group():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.patch("/api/groups/1", json={"description": "Updated"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"

def test_delete_group():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.delete("/api/groups/1")
    assert response.status_code == 204

def test_delete_group_not_found():
    response = client.delete("/api/groups/999")
    assert response.status_code == 404

def test_add_user_to_group():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.post("/api/groups/1/users/1")
    assert response.status_code == 201

def test_add_user_to_group_duplicate():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    client.post("/api/groups/1/users/1")
    response = client.post("/api/groups/1/users/1")
    assert response.status_code == 409

def test_remove_user_from_group():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    client.post("/api/groups/1/users/1")
    response = client.delete("/api/groups/1/users/1")
    assert response.status_code == 204

def test_get_group_users():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    client.post("/api/groups/1/users/1")
    response = client.get("/api/groups/1/users")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_group_not_found():
    response = client.patch("/api/groups/999", json={"name": "Ghost"})
    assert response.status_code == 404

def test_update_group_duplicate_name():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/groups", json={"name": "alpha-testers"})
    response = client.patch("/api/groups/2", json={"name": "beta-testers"})
    assert response.status_code == 409

def test_remove_user_from_group_not_found():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.delete("/api/groups/1/users/999")
    assert response.status_code == 404

def test_remove_user_group_not_found():
    response = client.delete("/api/groups/999/users/1")
    assert response.status_code == 404

def test_get_group_users_not_found():
    response = client.get("/api/groups/999/users")
    assert response.status_code == 404

def test_add_user_group_not_found():
    response = client.post("/api/groups/999/users/1")
    assert response.status_code == 404

def test_update_group_description_only():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.patch("/api/groups/1", json={"description": "Updated desc"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated desc"

def test_update_group_name_unique():
    client.post("/api/groups", json={"name": "beta-testers"})
    client.post("/api/groups", json={"name": "alpha-testers"})
    response = client.patch("/api/groups/1", json={"name": "gamma-testers"})
    assert response.status_code == 200
    assert response.json()["name"] == "gamma-testers"

def test_add_user_to_group_user_not_found():
    client.post("/api/groups", json={"name": "beta-testers"})
    response = client.post("/api/groups/1/users/999")
    assert response.status_code == 404