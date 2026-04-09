from datetime import datetime , timedelta, timezone

from fastapi import HTTPException, status

from jose import jwt, JWTError  # type: ignore

SECRET_KEY = 'YOUR SECRET KEY HERE'
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 30
REFRESH_EXPIRE_DAYS = 30

def _create_token(data: dict, expires_delta: timedelta) -> str: # _function_name refers to a private function that
                                                                #  shouldnt be called directly
    payload = data.copy()
    expiry = datetime.now(timezone.utc) + expires_delta

    payload["exp"] = expiry

    return jwt.encode(algorithm=ALGORITHM, key=SECRET_KEY, claims=payload)


def create_access_token(data: dict) -> str: # use this to generate an access token on successful authentication
    return _create_token(data, timedelta(minutes=ACCESS_EXPIRE_MINUTES))

def create_refresh_token(data: dict) -> str: # use this to generate a new access token when the previous one expires
    return _create_token(data, timedelta(days=REFRESH_EXPIRE_DAYS))


credential_exception = HTTPException( 
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)

def verify_token(token: str) -> dict: # TO verify token (authorization) 
    try:
        payload = jwt.decode(token=token, algorithms=[ALGORITHM],key=SECRET_KEY)
        sub = payload.get('sub')
        if sub is None:
            raise credential_exception
        return payload
    except JWTError:
        raise credential_exception

