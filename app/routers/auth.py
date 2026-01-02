from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.config import Settings, get_settings
from app.dependencies import get_db
from app.schemas.auth import TokenResponse, UserSingUp, UserSingIn, UserResponse
from app.services.auth_service import sign_in_user, sign_up_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/sign-in",
    summary="Sign in a user",
    response_description="JWT Token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
def sign_in(
    credentials: UserSingIn,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    try:
        return sign_in_user(credentials, db, settings)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.post(
    "/sign-up",
    summary="Sign up a user",
    response_description="Created user",
    response_model=UserResponse,
)
def sign_up(user: UserSingUp, db: Session = Depends(get_db)):
    return sign_up_user(user, db)
