from pydantic import BaseModel, ConfigDict, Field, EmailStr


class AuthCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email")


class TokenRequest(BaseModel):
    token: str = Field(..., description="Magic link token")


class OTPVerifyRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email")
    otp_code: str = Field(..., min_length=6, max_length=6)
