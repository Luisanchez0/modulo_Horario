import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SECRET = _required_env("JWT_SECRET")
ALGORITHM = "HS256"


def create_token(data):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=2)
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def create_activation_token(data, expires_minutes: int = 120):
    payload = data.copy()
    payload["scope"] = "activation"
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def verify_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def verify_activation_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None

    if payload.get("scope") != "activation":
        return None

    return payload
