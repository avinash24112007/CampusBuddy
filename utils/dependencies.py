from utils.jwt_handler import verify_token, credential_exception
from database import SessionLocal
from fastapi import Depends, Request
from utils.session_maker import make_db_session
from sqlalchemy.orm import Session
from models.credentials_models import Admin_Credentials, User_Credentials

admin_table = Admin_Credentials
user_table = User_Credentials 


def get_current_admin(request: Request, db: Session = Depends(make_db_session)):
    token = request.cookies.get("access_token")

    if token is None:
        raise credential_exception

    payload = verify_token(token=token)

    admin_id = payload.get('sub')

    if admin_id is None:
        raise credential_exception
    
    admin = db.query(admin_table).filter(admin_table.id == int(admin_id)).first()

    if admin is None:
        raise credential_exception
    return admin
    
def get_current_user(request: Request, db: Session = Depends(make_db_session)):
    token = request.cookies.get("access_token")
    print(f"TOKEN: {token}")

    if token is None:
        print("NO TOKEN FOUND")
        raise credential_exception

    payload = verify_token(token=token)
    print(f"PAYLOAD: {payload}")

    user_id = payload.get('sub')
    print(f"USER_ID: {user_id}")

    if user_id is None:
        print("NO SUB IN PAYLOAD")
        raise credential_exception

    user = db.query(user_table)\
                .filter(user_table.id == int(user_id)).first()
    print(f"USER FOUND: {user}")

    if user is None:
        print("USER NOT FOUND IN DB")
        raise credential_exception

    return user