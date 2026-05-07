from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.infrastructure.db.models  # noqa: F401
from src.core.config import settings
from src.infrastructure.db.base import Base
from src.infrastructure.db.postgres_migrations import drop_horarios_catalog_foreign_keys
from src.infrastructure.db.session import engine
from src.interfaces.api.routes import routers

app = FastAPI(
    title=settings.app_name,
    description="Microservicio de horarios escolares",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allow_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    drop_horarios_catalog_foreign_keys(engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


for router in routers:
    app.include_router(router)
