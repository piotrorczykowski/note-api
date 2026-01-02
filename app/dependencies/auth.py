from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlmodel import Session, select
from app.core.config import Settings, get_settings
from app.core.constants import JWT_ALGORITHM
from app.dependencies.db import get_db
from app.models.user import User
from sqlalchemy.orm import load_only

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
        user_id: int | None = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                load_only(
                    User.id,
                    User.email,
                    User.full_name,
                )
            )
        )
        user = db.exec(statement).one()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
