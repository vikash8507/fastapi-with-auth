from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.auth.model import User
from app.auth.schema import (
    AuthUserSchema,
    ChangePasswordSchema,
    ResetPasswordSchema,
    SendTokenSchema,
    SigninSchema,
    SignupSchema,
    TokenSchema,
    RefreshTokenSchema,
    VerifyEmailSchema
)
from app.database import get_db
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    create_verification_token,
    get_current_user,
    validate_refresh_token,
    verify_verification_token
)
from app.utils.hashing import HashPassword


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/signup", status_code=status.HTTP_200_OK)
def signup(request: SignupSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in used")
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in used")
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
    return {"detail": "Signup successfully!", "token": token}


@router.post("/signin", status_code=status.HTTP_200_OK, response_model=TokenSchema)
def signin(request: SigninSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong credentials")
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please verify your email")
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")
    password_context = HashPassword()
    if not password_context.verify_hash_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong credentials")
    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }


@router.get("/me", status_code=status.HTTP_200_OK, response_model=AuthUserSchema)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/token/refresh", status_code=status.HTTP_200_OK, response_model=TokenSchema)
def refresh_token(request: RefreshTokenSchema, db: Session = Depends(get_db)):
    user = validate_refresh_token(request, db)
    return {
        "access_token": create_access_token(user.username),
        "refresh_token": request.refresh_token,
    }


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    password_context = HashPassword()
    auth_user = db.query(User).filter(User.id == user.id).first()
    if request.password1 != request.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password1 and password2 must be same")
    if not password_context.verify_hash_password(request.current_password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password mis-match")
    if password_context.verify_hash_password(request.password1, auth_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password same as current password")
    auth_user.password = password_context.get_hash_password(request.password1)
    db.add(auth_user)
    db.commit()
    return {"detail": "Change password successfully!"}


@router.post("/email-verify", status_code=status.HTTP_200_OK)
def email_verify(request: VerifyEmailSchema, db: Session = Depends(get_db)):
    user = verify_verification_token(request.token)
    auth_user = db.query(User).filter(User.id == user.id).first()
    auth_user.verified = True
    auth_user.active = True
    db.add(auth_user)
    db.commit()
    return {"detail": "Email verified successfully!"}


@router.post("/resend-email", status_code=status.HTTP_200_OK)
def resend_email(request: SendTokenSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = create_verification_token(user.username)
    return {"detail": token}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: SendTokenSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = create_verification_token(user.username, token_type="reset")
    return {"detail": token}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordSchema, db: Session = Depends(get_db)):
    if request.password1 != request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password mis-match")
    user = verify_verification_token(request.token, token_type="reset")
    auth_user = db.query(User).filter(User.id == user.id).first()
    password_context = HashPassword()
    auth_user.password = password_context.get_hash_password(request.password1)
    db.add(auth_user)
    db.commit()
    return {"detail": "Reset password successfully!"}
