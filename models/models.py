from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base # Base is initialized in database.py
from datetime import datetime, timezone
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin' or 'student'
    is_active = Column(Boolean, default=True)
    
    enrollments = relationship("Enrollment", back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    code = Column(String, unique=True)
    capacity = Column(Integer)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)
    
    enrollments = relationship("Enrollment", back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class EnrollmentAudit(Base):
    __tablename__ = "enrollment_audit"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False) # e.g., "ENROLLED" or "DROPPED"
    user_id = Column(Integer, nullable=False)

    # Using a lambda for timezone-aware UTC time
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))