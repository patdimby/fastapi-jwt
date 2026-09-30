import time
import jwt
import pytest
import main
from app.auth.jwt_handler import JWT_SECRET, decode_JWT, signJWT
from app.auth.passwords import hash_password, verify_password

POST = {"title": "New post", "content": "Useful content"}

def test_public_reads(client):
    assert client.get("/").json() == {"message": "Hello World"}
    assert len(client.get("/posts").json()["data"]) == 3
    assert client.get("/posts/1").json()["title"] == "Penguins are awesome"
    assert client.get("/posts/999").status_code == 404

def test_signup_and_login_second_account(client, register):
    register()
    register("other@example.com")
    response = client.post("/users/login", json={"email": "other@example.com", "password": "secret123"})
    assert response.status_code == 200
    assert decode_JWT(response.json()["access token"])["userID"] == "other@example.com"
    assert all(user.get("password") is None for user in main.users)

@pytest.mark.parametrize("email,password", [("missing@example.com", "secret123"), ("ada@example.com", "wrong")])
def test_bad_credentials(client, register, email, password):
    register()
    assert client.post("/users/login", json={"email": email, "password": password}).status_code == 401

def test_duplicate_email(client, register):
    register()
    assert client.post("/users/signup", json={"fullname": "Ada", "email": "ada@example.com", "password": "secret123"}).status_code == 409

@pytest.mark.parametrize("body", [{}, {"fullname": "", "email": "bad", "password": "short"}, {"fullname": "Ada", "email": "ada@example.com", "password": "short"}])
def test_signup_validation(client, body):
    assert client.post("/users/signup", json=body).status_code == 422

def test_missing_login_body(client):
    assert client.post("/users/login").status_code == 422

def test_create_post(client, register):
    headers = register()
    assert client.post("/posts", headers=headers, json={**POST, "id": 200}).status_code == 200
    assert client.get("/posts/4").json() == {"id": 4, **POST}
    assert client.post("/posts", headers=headers, json={}).status_code == 422

@pytest.mark.parametrize("kind", ["missing", "malformed", "expired", "wrong-secret", "no-exp", "no-user"])
def test_invalid_tokens_cannot_create(client, kind):
    payload = {"userID": "ada@example.com", "exp": int(time.time()) + 3600}
    key = JWT_SECRET
    if kind == "expired": payload["exp"] = int(time.time()) - 1
    if kind == "wrong-secret": key = "wrong-secret-with-at-least-32-characters"
    if kind == "no-exp": payload.pop("exp")
    if kind == "no-user": payload.pop("userID")
    token = "garbage" if kind == "malformed" else jwt.encode(payload, key, algorithm="HS256")
    headers = {} if kind == "missing" else {"Authorization": "Bearer " + token}
    assert client.post("/posts", headers=headers, json=POST).status_code == 401
    assert len(main.posts) == 3

def test_user_list_requires_auth_and_excludes_secrets(client, register):
    assert client.get("/users").status_code == 401
    response = client.get("/users", headers=register())
    assert response.json() == {"data": [{"fullname": "Ada", "email": "ada@example.com"}]}

def test_hash_roundtrip_and_salt():
    first = hash_password("secret123")
    assert first != hash_password("secret123")
    assert verify_password("secret123", first)
    assert not verify_password("wrong", first)
    assert not verify_password("secret123", "bad")

def test_token_lifetime_and_claims():
    token = signJWT("ada@example.com")["access token"]
    payload = decode_JWT(token)
    assert payload["userID"] == "ada@example.com"
    assert 3500 < payload["exp"] - time.time() <= 3600
