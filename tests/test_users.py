def test_get_me_success(client):
    """ Success case: Valid JWT -> returns user profile"""
    # 1. Create a user
    user_data = {
        "name": "Profile User", 
        "email": "me@example.com", 
        "password": "password123", 
        "role": "student"
    }
    client.post("/auth/register", json=user_data)
    
    # 2. Log in to get the token
    login_res = client.post(
        "/auth/login",
        data={"username": "me@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    # 3. Access /users/me with the token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["name"] == "Profile User"

def test_get_me_no_token(client):
    """ No token: Missing JWT -> returns 401"""
    # No headers provided
    response = client.get("/users/me")
    
    # FastAPI/OAuth2 returns 401 Unauthorized for missing credentials
    assert response.status_code == 401

def test_get_me_invalid_token(client):
    """ Invalid token: Expired or malformed JWT -> returns 401"""
    headers = {"Authorization": "Bearer not-a-real-token"}
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == 401

def test_get_me_correct_user(client):
    """ Correct user: Ensure profile matches specifically the logged-in user"""
    # 1. Register two users
    client.post("/auth/register", json={"name": "User A", "email": "a@ex.com", "password": "weakpass", "role": "student"})
    client.post("/auth/register", json={"name": "User B", "email": "b@ex.com", "password": "weakpass", "role": "student"})
    
    # 2. Login as User B
    login_res = client.post("/auth/login", data={"username": "b@ex.com", "password": "weakpass"})
    token_b = login_res.json()["access_token"]
    
    # 3. Verify /me returns User B, not User A
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token_b}"})
    assert response.json()["email"] == "b@ex.com"
    assert response.json()["name"] == "User B"