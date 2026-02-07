from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: str = Field(..., pattern="^(student|admin)$")

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes = True)
