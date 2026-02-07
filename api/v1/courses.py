from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from api.deps import admin_required
import crud
from schemas import course
from models import models
router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=list[course.CourseOut])
def list_courses(
    skip: int = 0, # How many Courses to skip before starting to dispay
    limit: int = 10, # Courses to show per page
    search: str = None, # Search with keyword in Course title (Not case sensitive)
    db: Session = Depends(get_db)
):
    return crud.get_courses(db, skip=skip, limit=limit, search=search)

@router.get("/{id}", response_model=course.CourseOut)
def get_course(id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course: raise HTTPException(status_code=404, detail="Ooh no! Course not found")
    return course

@router.post("/", response_model=course.CourseOut)
def create_course(course_in: course.CourseCreate, admin=Depends(admin_required), db: Session = Depends(get_db)):
    return crud.create_course(db, course_in)

@router.patch("/{id}", response_model=course.CourseOut)
def update_course(id: int, course_in: course.CourseUpdate, db: Session = Depends(get_db), admin=Depends(admin_required)):

    db_course = db.query(models.Course).filter(models.Course.id == id).first()
    
    if not db_course:
        raise HTTPException(status_code=404, detail="Ooh no! Course not found")
        
    return crud.update_course(db, id, course_in)
        
@router.patch("/{id}/status", response_model=course.CourseOut)
def toggle_course_status(id: int, admin=Depends(admin_required), db: Session = Depends(get_db)):

    # 1. Execute the toggle logic
    db_course = crud.toggle_course(db, id)
    
    # 2. Check if the course actually existed
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 3. If it exists, return it (FastAPI will then validate it against CourseOut)
    return db_course