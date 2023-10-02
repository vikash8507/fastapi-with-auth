from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from app.auth.model import User
from app.auth.schema import (
    ChangePasswordSchema,
    ResetPasswordSchema,
    SendTokenSchema,
    SigninSchema,
    SignupSchema,
    VerifyEmailSchema,
)
from app.utils.auth import create_verification_token, verify_verification_token
from app.utils.hashing import HashPassword


def signup_repository(request: SignupSchema, db: Session):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in used"
        )
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in used"
        )
    password_context = HashPassword()
    hashed_password = password_context.get_hash_password(request.password)
    user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        email=request.email,
        password=hashed_password,
    )
    db.add(user)
    db.commit()
    token = create_verification_token(user.username)
    return token


def signin_repository(request: SigninSchema, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong credentials"
        )
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please verify your email"
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active"
        )
    password_context = HashPassword()
    if not password_context.verify_hash_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong credentials"
        )
    return user


def change_password_repository(request: ChangePasswordSchema, db: Session, user: User):
    password_context = HashPassword()
    auth_user = db.query(User).filter(User.id == user.id).first()
    if request.password1 != request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password1 and password2 must be same",
        )
    if not password_context.verify_hash_password(
        request.current_password, auth_user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password mis-match"
        )
    if password_context.verify_hash_password(request.password1, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password same as current password",
        )
    auth_user.password = password_context.get_hash_password(request.password1)
    db.add(auth_user)
    db.commit()


def verify_email_repository(request: VerifyEmailSchema, db: Session):
    user = verify_verification_token(request.token)
    auth_user = db.query(User).filter(User.id == user.id).first()
    auth_user.verified = True
    auth_user.active = True
    db.add(auth_user)
    db.commit()


def resend_verify_email_repository(request: SendTokenSchema, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    token = create_verification_token(user.username)
    return token


def forgot_password_repository(request: SendTokenSchema, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    token = create_verification_token(user.username, token_type="reset")
    return token


def reset_password_repository(request: ResetPasswordSchema, db: Session):
    if request.password1 != request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password mis-match"
        )
    user = verify_verification_token(request.token, token_type="reset")
    auth_user = db.query(User).filter(User.id == user.id).first()
    password_context = HashPassword()
    auth_user.password = password_context.get_hash_password(request.password1)
    db.add(auth_user)
    db.commit()
