from fastapi import HTTPException
from api.deps import get_current_user, admin_required

# --- Mocks ---

class MockUser:
    def __init__(self, id, role):
        self.id = id
        self.role = role
        self.email = f"user{id}@test.com"

async def mock_student():
    return MockUser(id=1, role="student")

async def mock_admin():
    return {"id": 99, "role": "admin"}

async def mock_forbidden():
    raise HTTPException(status_code=403, detail="Forbidden")

# --- Tests ---

## 1. Student Operations: POST /enrollments

def test_enroll_success(client, app):
    """ Success: Student enrolls in active course"""
    app.dependency_overrides[admin_required] = mock_admin
    c = client.post("/courses/", json={"title": "Math", "code": "M1", "capacity": 10, "is_active": True}).json()
    
    app.dependency_overrides[get_current_user] = mock_student
    response = client.post("/enrollments", json={"course_id": c["id"]})
    assert response.status_code == 200
    assert response.json()["course_id"] == c["id"]

def test_enroll_unauthorized_admin(client, app):
    """ Unauthorized: Admin tries to enroll as student"""
    app.dependency_overrides[get_current_user] = lambda: MockUser(id=99, role="admin")
    response = client.post("/enrollments", json={"course_id": 1})
    assert response.status_code == 403

def test_enroll_capacity_full(client, app):
    """ Capacity full: Returns 400"""
    app.dependency_overrides[admin_required] = mock_admin
    c = client.post("/courses/", json={"title": "Full", "code": "F1", "capacity": 1, "is_active": True}).json()
    
    # Enroll first student
    app.dependency_overrides[get_current_user] = lambda: MockUser(id=1, role="student")
    client.post("/enrollments", json={"course_id": c["id"]})
    
    # Second student tries
    app.dependency_overrides[get_current_user] = lambda: MockUser(id=2, role="student")
    response = client.post("/enrollments", json={"course_id": c["id"]})
    assert response.status_code == 400

def test_enroll_duplicate(client, app):
    """ Duplicate enrollment: Already enrolled → returns 409"""
    app.dependency_overrides[admin_required] = mock_admin
    c = client.post("/courses/", json={"title": "Dup Test", "code": "DUP1", "capacity": 10, "is_active": True}).json()
    
    app.dependency_overrides[get_current_user] = mock_student
    # First enrollment
    client.post("/enrollments", json={"course_id": c["id"]})
    
    # Second enrollment attempt
    response = client.post("/enrollments", json={"course_id": c["id"]})
    # Note: Ensure your crud.enroll_student raises 409 for duplicates
    assert response.status_code == 409
    assert "already enrolled" in response.json()["detail"].lower()

def test_enroll_nonexistent_course(client, app):
    """ Invalid course: Nonexistent course → returns 404"""
    app.dependency_overrides[get_current_user] = mock_student
    response = client.post("/enrollments", json={"course_id": 9999})
    assert response.status_code == 404

## 2. Student Operations: DELETE /enrollments/{course_id}

def test_drop_course_success(client, app):
    """ Success: Student drops course"""
    app.dependency_overrides[admin_required] = mock_admin
    c = client.post("/courses/", json={"title": "Drop", "code": "D1", "capacity": 5, "is_active": True}).json()
    
    app.dependency_overrides[get_current_user] = mock_student
    client.post("/enrollments", json={"course_id": c["id"]})
    
    response = client.delete(f"/enrollments/{c['id']}")
    assert response.status_code == 200

## 3. Admin Operations: GET /admin/enrollments

def test_admin_list_all_unauthorized(client, app):
    """ Unauthorized: Student tries admin route"""
    app.dependency_overrides[admin_required] = mock_forbidden
    response = client.get("/admin/enrollments")
    assert response.status_code == 403

def test_admin_list_success(client, app):
    """ Success: Admin lists all"""
    app.dependency_overrides[admin_required] = mock_admin
    response = client.get("/admin/enrollments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_get_course_enrollments_not_found(client, app):
    """ Invalid ID: Nonexistent course → returns 404"""
    app.dependency_overrides[admin_required] = mock_admin

    # Attempt to get enrollments for a course that doesn't exist
    response = client.get("/admin/courses/9999/enrollments")
    assert response.status_code == 404

## 4. Admin Operations: DELETE /admin/enrollments/{id}

def test_admin_remove_student_success(client, app):
    """ Success: Admin removes student via record ID"""

    # Setup: Create course and enrollment
    app.dependency_overrides[admin_required] = mock_admin
    c = client.post("/courses/", json={"title": "AdminDel", "code": "AD1", "capacity": 5}).json()
    app.dependency_overrides[get_current_user] = mock_student
    e = client.post("/enrollments", json={"course_id": c["id"]}).json()
    
    # Delete as admin
    app.dependency_overrides[admin_required] = mock_admin
    response = client.delete(f"/admin/enrollments/{e['id']}")
    assert response.status_code == 204

def test_admin_remove_student_unauthorized(client, app):
    """ Unauthorized: Student tries to delete an enrollment → returns 403"""

    # Override admin_required to simulate a failure/student role
    app.dependency_overrides[admin_required] = mock_forbidden
    
    response = client.delete("/admin/enrollments/1")
    assert response.status_code == 403

def test_admin_remove_nonexistent(client, app):
    """ Invalid ID: 404"""
    app.dependency_overrides[admin_required] = mock_admin
    response = client.delete("/admin/enrollments/9999")
    assert response.status_code == 404