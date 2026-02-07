from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from api.deps import get_current_user, admin_required
from schemas import enrollment
import crud
from models import models

router = APIRouter(tags=["Enrollments"])

# --- Student Endpoints ---
@router.post("/enrollments", response_model=enrollment.EnrollmentOut)
def enroll(
    data: enrollment.EnrollmentCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # Identity captured here
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can enroll")
        
    # Pass the ID from the token
    return crud.enroll_student(db, data.course_id, current_user.id)

@router.delete("/enrollments/{course_id}")
def drop_course(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.delete_own_enrollment(db, course_id, current_user.id)

# --- Admin Endpoints ---
@router.get("/admin/enrollments", response_model=list[enrollment.EnrollmentOut])
def view_all_enrollments(admin=Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()

@router.get("/admin/courses/{id}/enrollments", response_model=list[enrollment.EnrollmentOut])
def view_course_enrollments(id: int, admin=Depends(admin_required), db: Session = Depends(get_db)):
    # Check to see if the course exists
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    return db.query(models.Enrollment).filter(models.Enrollment.course_id == id).all()

@router.delete("/admin/enrollments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_remove_student(
    id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(admin_required) # Security layer
):
    deleted_record = crud.admin_delete_enrollment(db, id)
    if not deleted_record:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
    
    return None # 204 No Content: typically returns nothing