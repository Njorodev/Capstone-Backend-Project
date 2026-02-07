from api.deps import admin_required, get_current_user
from fastapi import HTTPException

# --- Mocks ---

async def mock_admin_required():
    return {"id": 1, "role": "admin"}

async def mock_admin_forbidden():
    # Simulating the behavior when a student hits an admin_required dependency
    raise HTTPException(status_code=403, detail="Not enough permissions")

# --- Tests ---

## 1. GET /courses/ (Public)

def test_list_active_courses_integrity(client, app):
    """ Success: Only active courses & Data integrity"""
    app.dependency_overrides[admin_required] = mock_admin_required
    client.post("/courses/", json={"title": "Active", "code": "A1", "capacity": 10, "is_active": True})
    client.post("/courses/", json={"title": "Inactive", "code": "I1", "capacity": 10, "is_active": False})
    
    response = client.get("/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    # Integrity check
    assert all(k in data[0] for k in ("id", "title", "code", "capacity", "is_active"))

def test_list_courses_empty(client):
    """ Empty list: No active courses"""
    response = client.get("/courses/")
    assert response.status_code == 200
    assert response.json() == []

## 2. GET /courses/{id} (Public)

def test_get_course_success(client, app):
    """ Success case: Valid ID"""
    app.dependency_overrides[admin_required] = mock_admin_required
    res = client.post("/courses/", json={"title": "Find Me", "code": "F1", "capacity": 5})
    c_id = res.json()["id"]
    
    response = client.get(f"/courses/{c_id}")
    assert response.status_code == 200
    assert response.json()["code"] == "F1"

def test_get_course_malformed_id(client):
    """ Malformed ID: String instead of int"""
    response = client.get("/courses/not-an-int")
    assert response.status_code == 422

## 3. POST /courses/ (Admin Only)

def test_create_course_unauthorized(client, app):
    """ Unauthorized: Student tries to create"""
    app.dependency_overrides[admin_required] = mock_admin_forbidden
    response = client.post("/courses/", json={"title": "Hack", "code": "H1", "capacity": 1})
    assert response.status_code == 403

def test_create_course_invalid_input(client, app):
    """ Invalid input: Missing fields"""
    app.dependency_overrides[admin_required] = mock_admin_required
    # Missing 'code' and 'capacity'
    response = client.post("/courses/", json={"title": "Incomplete"})
    assert response.status_code == 422

## 4. PATCH /courses/{id} (Admin Only)

def test_update_course_success(client, app):
    """ Success case: Admin updates course"""
    app.dependency_overrides[admin_required] = mock_admin_required
    res = client.post("/courses/", json={"title": "Old Title", "code": "OLD", "capacity": 10})
    c_id = res.json()["id"]
    
    response = client.patch(f"/courses/{c_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_update_course_unauthorized(client, app):
    """ Unauthorized: Student tries to update"""
    app.dependency_overrides[admin_required] = mock_admin_forbidden
    response = client.patch("/courses/1", json={"title": "Hacked"})
    assert response.status_code == 403

## 5. PATCH /courses/{id}/status (Admin Only)

def test_toggle_status_not_found(client, app):
    """ Invalid ID: Nonexistent course"""
    app.dependency_overrides[admin_required] = mock_admin_required
    
    response = client.patch("/courses/9999/status")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"