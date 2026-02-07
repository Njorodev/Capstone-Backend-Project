from fastapi import Depends, HTTPException, status
from models.models import User
from core.security import get_current_user

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stop There, What you are doing is illegal and can lead to permanent ban"
        )
    return current_user