from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from sqlmodel import Session, select
from app.core.config import Settings
from app.core.constants import JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.auth import TokenResponse, UserSingUp, UserSingIn


def sign_in_user(
    credentials: UserSingIn, db: Session, settings: Settings
) -> TokenResponse:
    statement = select(User).where(User.email == credentials.email)
    user = db.exec(statement).one()

    if not user:
        raise Exception("Invalid email or password")

    is_password_valid = bcrypt.checkpw(
        credentials.password.encode("utf-8"),
        user.password.encode("utf-8"),
    )
    if not is_password_valid:
        raise Exception("Invalid email or password")

    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"user_id": user.id, "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return TokenResponse(access_token=token)


def sign_up_user(user: UserSingUp, db: Session) -> User:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt).decode("utf-8")

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
