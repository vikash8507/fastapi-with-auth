from datetime import datetime, timedelta
from typing import Union, Any, Optional
from jose import jwt
from sqlalchemy.orm import Session


from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from jose import jwt
from pydantic import ValidationError
from app.auth.schema import RefreshTokenSchema, TokenPayload, VerificationTokenPayload
from app.database import get_db
from app.auth.model import User
from app.config import Settings

settings = Settings()

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
JWT_VERIFICATION_TOKEN = settings.JWT_VERIFICATION_TOKEN
JWT_RESET_TOKEN = settings.JWT_RESET_TOKEN

reuseable_oauth = HTTPBearer(scheme_name="JWT Bearer")


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expires_delta, "sub": str(subject), "token_type": "access"}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expires_delta, "sub": str(subject), "token_type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_user(token: str, db: Optional[Session] = None, check_for: str = "access"):
    SECRET_KEY = JWT_SECRET_KEY if check_for == "access" else JWT_REFRESH_SECRET_KEY
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_data.token_type != check_for:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db is None:
        db: Session = next(get_db())
    user = db.query(User).filter(User.username == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user


def get_current_user(token: HTTPAuthorizationCredentials = Depends(reuseable_oauth)):
    return get_user(token.credentials, check_for="access")


def validate_refresh_token(token: RefreshTokenSchema, db: Session):
    return get_user(token.refresh_token, db, check_for="refresh")


def create_verification_token(username: str, token_type: str = "verification"):
    SECRET_KEY = (
        JWT_VERIFICATION_TOKEN if token_type == "verification" else JWT_RESET_TOKEN
    )
    expires_delta = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expires_delta, "sub": str(username)}
    token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return token


def verify_verification_token(token: str, token_type: str = "verification"):
    SECRET_KEY = (
        JWT_VERIFICATION_TOKEN if token_type == "verification" else JWT_RESET_TOKEN
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = VerificationTokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError) as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db: Session = next(get_db())
    user = db.query(User).filter(User.username == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user
