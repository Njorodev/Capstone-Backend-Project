from fastapi import APIRouter, Depends
from api.deps import get_current_user
import schemas, models

router = APIRouter(prefix="/users", tags=["Users"])

# Router to get profile
@router.get("/me", response_model=schemas.user.UserOut)
def get_me(current_user: models.models.User = Depends(get_current_user)):
    return current_user