
#  Course Enrollment System (Capstone Backend)

A high-performance, secure FastAPI backend designed to manage University course enrollments. This project demonstrates modern API development practices, including **Role-Based Access Control (RBAC)**, **Audit Logging**, and **Rate Limiting**.

##  Project Structure

The project follows a modular architecture to ensure scannability and ease of maintenance.

```text
Capstone Backend Project/
├── api/
│   ├── v1/
│   │   ├── auth.py          # JWT Login & Registration (Rate Limited)
│   │   ├── courses.py       # Course CRUD (Admin & Student views)
│   │   ├── enrollments.py   # Enrollment/Drop logic with Audit Logs
│   │   └── users.py         # User profile management
│   └── limiter.py           # Rate limiting configuration (SlowAPI)
├── core/
│   ├── config.py            # App settings (Pydantic V2)
│   └── security.py          # JWT & Password hashing (Bcrypt)
├── models/
│   └── models.py            # SQLAlchemy Models (User, Course, Audit)
├── schemas/
│   ├── course.py            # Pydantic models for Courses
│   ├── user.py              # Pydantic models for Users
│   └── enrollment.py        # Pydantic models for Enrollments
├── tests/
│   ├── conftest.py          # Pytest fixtures & Database isolation
│   ├── test_auth.py         # Auth & Rate limit tests
│   ├── test_courses.py      # Course management tests
│   └── test_enrollments.py  # Enrollment logic tests
├── app.py                   # Main FastAPI entry point & Middleware
├── database.py              # Session & Engine setup
├── crud.py                  # Database operations (Business Logic)
├── seed.py                  # Mock data generation script
└── requirements.txt         # Project dependencies

```

---

##  Key Features & Bonuses

* **Security Stack**: JWT Authentication + Password hashing with `Passlib`.
* **Rate Limiting**: The `/auth/login` endpoint is protected by `slowapi` (5 requests/minute) to prevent brute-force attacks.
* **Audit Trail**: Every enrollment action is captured in an `EnrollmentAudit` table, logging the `action`, `user_id`, and `timestamp`.
* **Professional Soft Deletes**: Instead of deleting records, the system uses a `deleted_at` timestamp. This preserves data integrity for historical reporting.
* **Pagination**: Course listing supports `skip` and `limit` parameters for efficient data fetching.
* **Pydantic V2**: Fully migrated to the latest Pydantic standards (using `model_config` and `model_dump`).
* **Database Migrations**: For this version, schema changes are handled by recreating the SQLite database. In a production environment, Alembic would be used to handle schema evolution and data migrations to ensure zero-downtime updates.
---

##  Tech Stack

* **Framework**: FastAPI
* **Database**: SQLite (SQLAlchemy 2.0 ORM)
* **Validation**: Pydantic V2
* **Testing**: Pytest & HTTPX
* **Limiting**: SlowAPI

---

##  Installation & Setup

1. **Clone & Navigate:**
```bash
cd "Capstone Backend Project"

```

2. **Setup Virtual Environment:**
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate

```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt

```

4. **Seed the Database:**
This creates the tables and populates the system with 20 demo courses.
```bash
python seed.py

```

5. **Run the Server:**
```bash
uvicorn app:app --reload

```

---

##  Testing

The project includes a robust test suite covering 33 edge cases, including capacity checks and role permissions.

```bash
pytest -v

```

---

###  API Endpoint Reference

| Method | Endpoint | Description | Access |
| --- | --- | --- | --- |
| **Authentication** |  |  |  |
| `POST` | `/auth/register` | Register a new student or admin account | Public |
| `POST` | `/auth/login` | Obtain JWT access token (Rate Limited) | Public |
| **User Profile** |  |  |  |
| `GET` | `/users/me` | Retrieve current logged-in user details | Authenticated |
| **Course Management** |  |  |  |
| `GET` | `/courses/` | List all courses (Supports `skip`, `limit`, `search`) | Public |
| `POST` | `/courses/` | Create a new course entry | **Admin Only** |
| `GET` | `/courses/{id}` | Get detailed information for a specific course | Public |
| `PATCH` | `/courses/{id}` | Update course details (title, code, capacity) | **Admin Only** |
| `PATCH` | `/courses/{id}/status` | Toggle course availability (Active/Inactive) | **Admin Only** |
| **Enrollments** |  |  |  |
| `POST` | `/enrollments` | Enroll current student in a course | **Student Only** |
| `DELETE` | `/enrollments/{course_id}` | Drop a course for the current student | **Student Only** |
| **Admin Operations** |  |  |  |
| `GET` | `/admin/enrollments` | View all system-wide enrollments | **Admin Only** |
| `GET` | `/admin/courses/{id}/enrollments` | View students enrolled in a specific course | **Admin Only** |
| `DELETE` | `/admin/enrollments/{id}` | Force-remove a student from a course | **Admin Only** |

---

##  Bonus Implementation Notes

* **Timestamp Soft Deletes**: We chose `deleted_at` (DateTime) over a simple Boolean to provide better insights into *when* data was removed.
* **Circular Import Resolution**: Used a standalone `api/limiter.py` to decouple the rate limiter from the main app instance.
* **Search with Title Keyword**: Used `search: str = None` query parameter to search courses with such Keywords. *NOT Case Sensitive*

---
