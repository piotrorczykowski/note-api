from pydantic import BaseModel, EmailStr, Field


class UserSingIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=64)


class UserSingUp(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
