from fastapi import APIRouter, Depends
from schemas.user_schemas import UserContextOut
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/profile", response_model=UserContextOut)
def get_profile(current_user = Depends(get_current_user)):
    return current_user
