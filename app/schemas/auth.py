from pydantic import BaseModel


class UserSingIn(BaseModel):
    email: str
    password: str


class UserSingUp(BaseModel):
    email: str
    full_name: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
