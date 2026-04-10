from fastapi import APIRouter, Depends, Query
from schemas.user_schemas import UserContextOut, UserSearchResponse
from utils.dependencies import get_current_user
from models.user_models import User
from sqlalchemy.orm import Session
from sqlalchemy import or_
from utils.session_maker import make_db_session

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/profile", response_model=UserContextOut)
def get_profile(current_user = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=UserSearchResponse)
def search_students(
    query: str = Query(..., min_length=1),
    db: Session = Depends(make_db_session),
    current_user = Depends(get_current_user)
):
    users = db.query(User).filter(
        or_(
            User.name.ilike(f"%{query}%"),
            User.department.ilike(f"%{query}%"),
            User.course.ilike(f"%{query}%")
        )
    ).all()
    return UserSearchResponse(success=True, data=users)
