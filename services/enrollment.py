from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import models


def enroll_student(db: Session, course_id: int, user_id: int):

    # 1. Fetch the course
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # 2. Rule: Enrollment fails if the course is inactive
    if not course.is_active:
        raise HTTPException(
            status_code=400, 
            detail="Cannot enroll in an inactive course"
        )

    # 3. Rule: A student cannot enroll in the same course twice
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user_id,
        models.Enrollment.course_id == course_id
    ).first()
    if existing_enrollment:
        raise HTTPException(
            status_code=400, 
            detail="You are already enrolled in this course"
        )

    # 4. Rule: Enrollment fails if the course is full
    current_enrollments_count = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id
    ).count()
    
    if current_enrollments_count >= course.capacity:
        raise HTTPException(
            status_code=400, 
            detail="Course is at full capacity"
        )

    # 5. Success: Create the enrollment
    new_enrollment = models.Enrollment(user_id=user_id, course_id=course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment