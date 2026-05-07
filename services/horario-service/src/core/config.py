from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _cors_allow_origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ALLOW_ORIGINS")
    if raw:
        parsed = tuple(origin.strip() for origin in raw.split(",") if origin.strip())
        if parsed:
            return parsed
    return (
        "http://localhost:5173",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
    )


@dataclass(frozen=True)
class Settings:
    database_url: str = _required_env("DATABASE_URL")
    app_name: str = os.getenv("APP_NAME", "horario-service")
    debug: bool = _to_bool(os.getenv("DEBUG"), False)
    usuarios_service_url: str = os.getenv("USUARIOS_SERVICE_URL", "http://localhost:8001")
    materias_service_url: str = os.getenv("MATERIAS_SERVICE_URL", "http://localhost:8002")
    aulas_service_url: str = os.getenv("AULAS_SERVICE_URL", "http://localhost:8003")
    internal_api_key: str = _required_env("INTERNAL_API_KEY")
    upstream_timeout_seconds: float = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5"))
    cors_allow_origins: tuple[str, ...] = _cors_allow_origins()


settings = Settings()
