from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CourseBase(BaseModel):
    title: str
    code: str
    capacity: int = Field(..., gt=0)
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None