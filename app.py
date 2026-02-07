from fastapi import FastAPI
from database import engine, Base
from api.v1 import auth, users, courses, enrollments
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Course Enrollment API",
    description="A secure, role-based platform for university enrollments.",
    version="1.0.0"
)

# handle rate limmiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

@app.get("/")
def General():
    return {"message": "Welcome to the Course Enrollment API. Visit /docs for Swagger UI."}