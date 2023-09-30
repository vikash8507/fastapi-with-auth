from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.model import User
from app.auth.repository import (
    change_password_repository,
    forgot_password_repository,
    resend_verify_email_repository,
    reset_password_repository,
    signin_repository,
    signup_repository,
    verify_email_repository
)
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
    get_current_user,
    validate_refresh_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/signup", status_code=status.HTTP_200_OK)
def signup(request: SignupSchema, db: Session = Depends(get_db)):
    token = signup_repository(request, db)
    return {"detail": "Signup successfully!", "token": token}


@router.post("/signin", status_code=status.HTTP_200_OK, response_model=TokenSchema)
def signin(request: SigninSchema, db: Session = Depends(get_db)):
    user = signin_repository(request, db)
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
    change_password_repository(request, db, user)
    return {"detail": "Change password successfully!"}


@router.post("/email-verify", status_code=status.HTTP_200_OK)
def email_verify(request: VerifyEmailSchema, db: Session = Depends(get_db)):
    verify_email_repository(request, db)
    return {"detail": "Email verified successfully!"}


@router.post("/resend-email", status_code=status.HTTP_200_OK)
def resend_email(request: SendTokenSchema, db: Session = Depends(get_db)):
    token = resend_verify_email_repository(request, db)
    return {"detail": token}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(request: SendTokenSchema, db: Session = Depends(get_db)):
    token = forgot_password_repository(request, db)
    return {"detail": token}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordSchema, db: Session = Depends(get_db)):
    reset_password_repository(request, db)
    return {"detail": "Reset password successfully!"}
