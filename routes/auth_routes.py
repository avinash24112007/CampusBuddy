from fastapi import FastAPI, APIRouter, Depends, Response, Request

from utils.session_maker import make_db_session
from utils.security import verify_password, hash_password
from utils.jwt_handler import create_access_token, create_refresh_token, credential_exception, HTTPException, verify_token

from models.credentials_models import Admin_Credentials
from models.user_models import User
from models.refresh_token import Admin_Refresh_Token, User_Refresh_Token

from schemas.auth_s import pyd_login, pyd_register

from datetime import datetime, timezone, timedelta

# 1. You MUST define 'app' here so Uvicorn can find it
app = FastAPI(title="CampusBuddy API")

router = APIRouter(prefix="/auth", tags=["Auth"])

@app.get("/")
def read_root():
    return {"status": "API is running"}

REFRESH_EXPIRE_DAYS = 7
router = APIRouter()
import base64
import hashlib
import os
import secrets
from email.mime.text import MIMEText

import redis
from fastapi import HTTPException, status
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
OTP_EXPIRY_SECONDS = 300  
MAX_ATTEMPTS = 5

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def send_otp_email(to_email: str, otp: str):
    service = get_gmail_service()
    body = f"Hello,\n\nYour verification code is: {otp}\n\nIt expires in 5 minutes."

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = "Your Verification Code"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw_message})
        .execute()
    )

class SendOTPRequest(BaseModel):
    email: EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    course: str
    department: str
    semester: str
    college_id: str
    otp: str  # Added OTP field to complete registration in one step


@router.post("/send-otp")
def send_verify_otp(request: SendOTPRequest, db: Session = Depends(make_db_session)
):
    email = str(request.email).lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    otp_key = f"otp:{email}"
    attempts_key = f"otp_attempts:{email}"

    pipeline = redis_client.pipeline()
    pipeline.set(otp_key, otp_hash, ex=OTP_EXPIRY_SECONDS)
    pipeline.set(attempts_key, 0, ex=OTP_EXPIRY_SECONDS)
    pipeline.execute()

    try:
        send_otp_email(email, otp)
    except Exception:
        redis_client.delete(otp_key, attempts_key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email",
        )

    return {"status": "success", "message": "OTP sent successfully"}


@router.post("/register")
def register(
    request: RegisterRequest, db: Session = Depends(make_db_session)
):
    email = str(request.email).lower()

    # 1. Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 2. Verify OTP from Redis
    otp_key = f"otp:{email}"
    attempts_key = f"otp_attempts:{email}"

    stored_hash = redis_client.get(otp_key)
    attempts = redis_client.get(attempts_key)

    if stored_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not found or has expired",
        )

    attempts_count = int(attempts) if attempts is not None else 0
    if attempts_count >= MAX_ATTEMPTS:
        redis_client.delete(otp_key, attempts_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect OTP attempts. Please request a new code.",
        )

    input_hash = hash_otp(request.otp)
    if not secrets.compare_digest(input_hash, stored_hash):
        redis_client.incr(attempts_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    redis_client.delete(otp_key, attempts_key)

    hashed_pw = hash_password(request.password)
    new_user = User(
        name=request.name,
        email=email,
        password=hashed_pw,
        phone=request.phone,
        course=request.course,
        department=request.department,
        semester=request.semester,
        college_id=request.college_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "Registration successful!",
        "user_id": str(new_user.id),
    }

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
