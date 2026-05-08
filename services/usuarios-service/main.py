from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import os
from src.interfaces.api.routes import auth_routes, docente_routes
from src.infrastructure.db.connection import engine, ensure_docentes_matricula_column, ensure_docentes_turno_column
from src.infrastructure.db.models import Base


def _cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
    ]

app = FastAPI(
    title="Usuarios Docentes Service",
    description="Microservicio para gestión de docentes en sistema educativo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta de nuevo más tarde."}
    )

security = HTTPBearer()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    ensure_docentes_turno_column()
    ensure_docentes_matricula_column()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(docente_routes.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "usuarios-service"}
