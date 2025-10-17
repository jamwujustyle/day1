from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import JWTError, jwt
from app.configs.settings import get_settings

settings = get_settings()
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE)

    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[dict]:
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.get("type") != "access":
        return None

    return payload


def verify_refresh_token(token: str) -> Optional[dict]:
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload
