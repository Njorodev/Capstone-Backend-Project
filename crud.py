from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import models
from schemas import course, user
from datetime import datetime


# Setup password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- UTILITY FUNCTIONS ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- USER CRUD ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(db: Session, user: user.UserCreate):
    """
    Handles User Registration (Requirement 1.1)
    """
    hashed_pwd = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pwd,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- COURSE CRUD ---

def create_course(db: Session, course: course.CourseCreate):
    """
    Admin-only: Create a course (Requirement 2.2)
    """
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, course_id: int, course_in: course.CourseUpdate):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    
    # Extract the data sent in the request (exclude unset fields)
    update_data = course_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

def toggle_course(db: Session, course_id: int):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course:
        db_course.is_active = not db_course.is_active
        db.commit()
        db.refresh(db_course)
    return db_course

def get_courses(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(models.Course).filter(models.Course.is_active == True)
    if search:
        query = query.filter(models.Course.title.contains(search))
    return query.offset(skip).limit(limit).all()
def enroll_student(db: Session, course_id: int, user_id: int):
    # 1. Check if course exists and is active
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_active:
        raise HTTPException(status_code=400, detail="Cannot enroll in an inactive course")

    # 2. Check if student is already enrolled
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.user_id == user_id
    ).first()
    if existing_enrollment:
        raise HTTPException(status_code=409, detail="You are already enrolled in this course")

    # 3. Check Capacity
    current_enrolled_count = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id
    ).count()
    
    if current_enrolled_count >= course.capacity:
        raise HTTPException(status_code=400, detail="Course is full")

    # 4. Perform Enrollment
    new_enrollment = models.Enrollment(course_id=course_id, user_id=user_id)
    db.add(new_enrollment)
    
    # We flush here to get the new_enrollment.id without finishing the transaction yet
    db.flush() 

    # 5. Create Audit Log
    audit_log = models.EnrollmentAudit(
        enrollment_id=new_enrollment.id, 
        action="ENROLLED", 
        user_id=user_id
    )
    db.add(audit_log)
    
    # Final commit for both Enrollment and Audit Log
    db.commit()
    db.refresh(new_enrollment)
    
    return new_enrollment

def delete_own_enrollment(db: Session, course_id: int, user_id: int):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.user_id == user_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
        
    db.delete(enrollment)
    db.commit()
    return {"message": "Successfully dropped the course"}

def admin_delete_enrollment(db: Session, enrollment_id: int):
    # Find the specific enrollment record by its ID
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    
    if not db_enrollment:
        return None  # The router will handle the 404 based on this
        
    db.delete(db_enrollment)
    db.commit()
    return db_enrollment

def soft_delete_course(db: Session, course_id: int):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course:
        course.deleted_at = datetime.utcnow()
        db.commit()
    return course