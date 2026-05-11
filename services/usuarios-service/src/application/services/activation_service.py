import os

from src.infrastructure.email.smtp_client import send_activation_email
from src.infrastructure.security.jwt import create_activation_token


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "https://modulo-horario.vercel.app").rstrip("/")


def _activation_expiry_minutes() -> int:
    raw = os.getenv("ACTIVATION_TOKEN_EXPIRE_MINUTES", "120")
    try:
        return max(5, int(raw))
    except ValueError:
        return 120


def build_activation_link(token: str) -> str:
    return f"{_frontend_url()}/activar?token={token}"


def send_activation_for_docente(docente) -> bool:
    token = create_activation_token(
        {"sub": str(docente.id), "correo": docente.correo},
        expires_minutes=_activation_expiry_minutes(),
    )
    activation_url = build_activation_link(token)
    return send_activation_email(docente.correo, getattr(docente, "nombre", ""), activation_url)
