from fastapi.testclient import TestClient
import src.storage as storage
from src.main import app

client = TestClient(app)

def setup_function():
    # Réinitialiser le storage avant chaque test
    storage.users.clear()
    storage.next_user_id = 1

def test_create_user():
    response = client.post("/api/users", json={
        "email": "alice@example.com",
        "name": "Alice",
        "role": "user"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert response.json()["id"] == 1

def test_create_user_duplicate_email():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.post("/api/users", json={"email": "alice@example.com", "name": "Alice2", "role": "user"})
    assert response.status_code == 409

def test_get_users():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_user():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_get_user_not_found():
    response = client.get("/api/users/999")
    assert response.status_code == 404

def test_update_user():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.patch("/api/users/1", json={"name": "Alice Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Updated"

def test_delete_user():
    client.post("/api/users", json={"email": "alice@example.com", "name": "Alice", "role": "user"})
    response = client.delete("/api/users/1")
    assert response.status_code == 204

def test_delete_user_not_found():
    response = client.delete("/api/users/999")
    assert response.status_code == 404