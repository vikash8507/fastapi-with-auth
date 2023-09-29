from pydantic import BaseModel, validator, Field, EmailStr


class BaseUserSchema(BaseModel):
    first_name: str = Field(max_length=20, min_length=2)
    last_name: str = Field(max_length=20, min_length=2)
    username: str = Field(max_length=15, min_length=6)
    email: EmailStr = Field(max_length=50)

    @validator("email")
    def email_validator(cls, value):
        return value


class SignupSchema(BaseUserSchema):
    password: str = Field(max_length=20, min_length=8)

    @validator("password")
    def password_validator(cls, value):
        return value


class AuthUserSchema(BaseUserSchema):
    class Config:
        from_attributes = True


class ChangePasswordSchema(BaseModel):
    current_password: str = Field(max_length=20, min_length=8)
    password1: str = Field(max_length=20, min_length=8)
    password2: str = Field(max_length=20, min_length=8)


class SigninSchema(BaseModel):
    email: EmailStr = Field(max_length=50)
    password: str = Field(max_length=20, min_length=8)


class SendTokenSchema(BaseModel):
    email: EmailStr


class VerifyEmailSchema(BaseModel):
    token: str


class ResetPasswordSchema(VerifyEmailSchema):
    password1: str = Field(max_length=20, min_length=8)
    password2: str = Field(max_length=20, min_length=8)


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class VerificationTokenPayload(BaseModel):
    exp: int
    sub: str


class TokenPayload(VerificationTokenPayload):
    token_type: str
