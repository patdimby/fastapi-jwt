import os
os.environ["secret"] = "test-only-signing-secret-longer-than-32-bytes"
os.environ["algorithm"] = "HS256"
import pytest
from fastapi.testclient import TestClient
import main

@pytest.fixture
def client():
    original = [dict(post) for post in main.posts]
    main.users.clear()
    with TestClient(main.app) as client:
        yield client
    main.posts[:] = original
    main.users.clear()

@pytest.fixture
def register(client):
    def create(email="ada@example.com"):
        response = client.post("/users/signup", json={"fullname": "Ada", "email": email, "password": "secret123"})
        assert response.status_code == 200
        return {"Authorization": "Bearer " + response.json()["access token"]}
    return create
