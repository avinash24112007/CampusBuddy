from utils.jwt_handler import verify_token, create_access_token, credential_exception
from fastapi import Depends, Request, Response
from utils.session_maker import make_db_session
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from models.credentials_models import Admin_Credentials
from models.user_models import User
from models.refresh_token import Admin_Refresh_Token, User_Refresh_Token

admin_table = Admin_Credentials
user_table = User

def _extract_token(request: Request) -> str | None:
    """Extract access token from Authorization header first, then fall back to cookies.
    This dual strategy handles both cross-domain (HF Spaces) and same-origin deployments."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header[7:]
    return request.cookies.get("access_token")

def auto_refresh_token(request: Request, response: Response, db: Session, payload: dict, role: str):
    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return

    exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    # If the token expires in less than 5 minutes
    if exp_time - datetime.now(timezone.utc) < timedelta(minutes=5):
        refresh_cookie = request.cookies.get("refresh_token")
        if not refresh_cookie:
            return
            
        model_cls = Admin_Refresh_Token if role == 'admin' else User_Refresh_Token
        ref_db = db.query(model_cls).filter(model_cls.token == refresh_cookie).first()
        
        # Only refresh if the refresh token is valid in the database
        if ref_db and ref_db.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            new_data = {
                'sub': payload.get('sub'),
                'email': payload.get('email', ''),
                'role': role
            }
            new_access = create_access_token(new_data)
            response.set_cookie(key='access_token', value=new_access, httponly=True, secure=True, samesite='none')


def get_current_admin(request: Request, response: Response, db: Session = Depends(make_db_session)):
    token = _extract_token(request)

    if token is None:
        raise credential_exception

    payload = verify_token(token=token)
    admin_id = payload.get('sub')
    role = payload.get('role')

    if admin_id is None:
        raise credential_exception
    
    # Reject non-admin tokens immediately so we never try to cast a UUID to int
    if role != 'admin':
        raise credential_exception

    try:
        admin = db.query(admin_table).filter(admin_table.id == int(admin_id)).first()
    except (ValueError, TypeError):
        raise credential_exception

    if admin is None:
        raise credential_exception
        
    auto_refresh_token(request, response, db, payload, role='admin')
    return admin
    
def get_current_user(request: Request, response: Response, db: Session = Depends(make_db_session)):
    token = _extract_token(request)

    if token is None:
        raise credential_exception

    payload = verify_token(token=token)
    user_id = payload.get('sub')

    if user_id is None:
        raise credential_exception

    role = payload.get('role')
    
    # Reject admin tokens from accessing student-only resources
    if role != 'user':
        raise credential_exception

    # User.id is a UUID, allowing direct mapping lookup without integer crashing!
    user = db.query(user_table).filter(user_table.id == user_id).first()

    if user is None:
        raise credential_exception
        
    auto_refresh_token(request, response, db, payload, role='user')
    return user