import pytest
from jose import jwt
from core.config import settings
from core.security import verify_password 
from models.models import User

## --- Registration Tests ---

def test_register_success(client):
    """ Success case: Register with valid data -> returns user object"""
    payload = {
        "name": "New Student",
        "email": "new@example.com",
        "password": "securepassword123",
        "role": "student"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200 
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "student"  # Role assignment check

def test_register_duplicate_email(client):
    """ Duplicate user: Register with existing email"""
    payload = {
        "name": "User 1",
        "email": "duplicate@example.com",
        "password": "password123",
        "role": "student"
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_register_invalid_input(client):
    """ Invalid input: Missing fields (422)"""
    response = client.post("/auth/register", json={"name": "No Email User"})
    assert response.status_code == 422

def test_password_is_hashed(client, db_session):
    """ Security: Password is hashed in DB"""
    password = "secret_password"
    client.post("/auth/register", json={
        "name": "Secure User",
        "email": "secure@example.com",
        "password": password,
        "role": "student"
    })
    db_user = db_session.query(User).filter(User.email == "secure@example.com").first()
    assert db_user.hashed_password != password
    assert verify_password(password, db_user.hashed_password)

## --- Login Tests ---

def test_login_success(client):
    """ Success case: Valid credentials -> returns 200 + JWT"""
    user_data = {"name": "Login User", "email": "login@example.com", "password": "password", "role": "admin"}
    client.post("/auth/register", json=user_data)
    
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    
    #  Token validity check
    payload = jwt.decode(data["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("sub") == "login@example.com"

def test_login_wrong_password(client):
    """ Wrong password: returns 400 """
    client.post("/auth/register", json={
        "name": "User", "email": "wrongpass@example.com", "password": "correct", "role": "student"
    })
    response = client.post(
        "/auth/login",
        data={"username": "wrongpass@example.com", "password": "incorrect"}
    )
    assert response.status_code == 400

def test_login_invalid_input(client):
    """ Invalid login: Missing password field"""
    response = client.post("/auth/login", data={"username": "test@example.com"})
    assert response.status_code == 422

    ##------Test for Rate limmitting-------

def test_login_rate_limiting(client):
    """ Rate Limit: Too many login attempts return 400"""
    user_data = {"username": "rate@test.com", "password": "password"}
    # Manually provide an IP so the limiter has a 'key' to track
    headers = {"X-Remote-Addr": "127.0.0.1"}

    for _ in range(5):
        client.post("/auth/login", data=user_data, headers=headers)

    response = client.post("/auth/login", data=user_data, headers=headers)
    
    assert response.status_code == 400