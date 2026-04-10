from fastapi import APIRouter, Depends, Response, Request

from sqlalchemy.orm import Session

from utils.session_maker import make_db_session
from utils.security import verify_password, hash_password
from utils.jwt_handler import create_access_token, create_refresh_token, credential_exception, HTTPException, verify_token

from models.credentials_models import Admin_Credentials
from models.user_models import User
from models.refresh_token import Admin_Refresh_Token, User_Refresh_Token

from schemas.auth_s import pyd_login, pyd_register

from datetime import datetime, timezone, timedelta

REFRESH_EXPIRE_DAYS = 7
router = APIRouter()


@router.post('/register')
def register(request: pyd_register, db: Session = Depends(make_db_session)):
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_pw = hash_password(request.password)
    new_user = User(
        name=request.name,
        email=request.email,
        password=hashed_pw,
        phone=request.phone,
        course=request.course,
        department=request.department,
        semester=request.semester,
        college_id=request.college_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Registration successful!", "user_id": str(new_user.id)}


@router.post('/login')
def login(response: Response, request: pyd_login,  db: Session = Depends(make_db_session)):
    instance = db.query(Admin_Credentials).filter(Admin_Credentials.email==request.email).first()

    if instance:
        true_password = instance.password

        is_valid = verify_password(hashed_password=true_password, password=request.password)

        if is_valid:
            data = {
                'sub' : str(instance.id),
                'email' : str(instance.email),
                'iat': datetime.now(timezone.utc),
                'role': 'admin'
            }

            access_token = create_access_token(data)
            refresh_token = create_refresh_token(data)

                       # Adding refresh token to admin refresh token table
            new_refresh_token = Admin_Refresh_Token(
                admin_id = instance.id,
                token = refresh_token,
                expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS)
            )

            db.add(new_refresh_token)
            db.commit()

            # Set cookies (works same-origin) + return tokens in body (works cross-domain)
            response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite='none')
            response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True, samesite='none')
            return {
                    "status": "success",
                    "message": "Login successful!",
                    "role": "admin",
                    "access_token": access_token,
                    "refresh_token": refresh_token
                    }
                        
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")
    else:
        # Get the user object with the corresponding email
        user_creds = User
        instance = db.query(user_creds).filter(user_creds.email==request.email).first()
        # Check if user exists
        if instance is None:
            raise HTTPException(status_code=404, detail="User not found")
        if instance:
            true_password = instance.password
            
            #Check the password with the actual password
            is_valid = verify_password(password=request.password,hashed_password=str(true_password))

            if is_valid:
                # Initialize the token payload
                data = {
                    'sub' : str(instance.id),
                    'email': str(instance.email),
                    'iat': datetime.now(timezone.utc),
                    'role' : 'user'
                }

                # Initializing the access and refresh token for user
                access_token = create_access_token(data=data)
                refresh_token = create_refresh_token(data)

                new_refresh_token = User_Refresh_Token(
                    user_id = instance.id,
                    token = refresh_token,
                    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS)
                )

                db.add(new_refresh_token)
                db.commit()

                # Set cookies (works same-origin) + return tokens in body (works cross-domain)
                response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite='none')
                response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True, samesite='none')
                
                return  {"status": "success", 
                         "message": "Login successful!", 
                         "role": "user",
                         "access_token": access_token,
                         "refresh_token": refresh_token}
            else:
                raise HTTPException(status_code=401, detail="Incorrect password") 
        else:
            raise HTTPException(status_code=404, detail="User not found")

@router.post('/logout/admin')
def logout_a(response: Response, request: Request,db: Session = Depends(make_db_session)):
    refresh_token = request.cookies.get("refresh_token")

    adm_ref_tk = Admin_Refresh_Token
    token = db.query(adm_ref_tk).filter(adm_ref_tk.token==refresh_token).first()

    if token:
        db.delete(token)
        
        
        db.commit()
        
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return {'status': 'success', 'message': "Logout Successful"}

@router.post('/logout/user')
def logout_u(response: Response, request: Request,db: Session = Depends(make_db_session)):
    refresh_token = request.cookies.get("refresh_token")

    usr_ref_tk = User_Refresh_Token
    token = db.query(usr_ref_tk).filter(usr_ref_tk.token==refresh_token).first()

    if token:
        db.delete(token)
        
        
        db.commit()
        
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return {'status': 'success', 'message': "Logout Successful"}

@router.post('/refresh')
def refresh(response: Response, request: Request, db: Session = Depends(make_db_session)):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh Token not in cookies")
    
    payload = verify_token(token=refresh_token)

    sub = payload.get('sub')
    role = payload.get('role')
    
    if role == 'admin':
        model_cls = Admin_Refresh_Token
    else:
        model_cls = User_Refresh_Token

    token = db.query(model_cls).filter(model_cls.token==refresh_token).first()

    if token is None:
        raise HTTPException(status_code=401, detail="Refresh Token not found in DB")
    current_time = datetime.now(timezone.utc)
    if token.expires_at.replace(tzinfo=timezone.utc) < current_time:
        raise credential_exception
    data =  {
                    'sub' : sub,
                    'role' : role
                }
    new_access_token = create_access_token(data)

    response.set_cookie(key='access_token', value=new_access_token, httponly=True, secure=True, samesite='none')

    return {'status': 'success', 'message': 'Token refreshed'}

