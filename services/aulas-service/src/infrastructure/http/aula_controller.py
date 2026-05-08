import os

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from src.application.service.aula_service import AulaService
from src.infrastructure.db.aula_repository_impl import AulaRepositoryImpl

load_dotenv()

app = FastAPI(title='Aulas Service', description='Microservicio para gestionar aulas')


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


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


USUARIOS_SERVICE_URL = os.getenv("USUARIOS_SERVICE_URL", "http://localhost:8001")
UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5"))


def _require_admin(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")

    url = f"{USUARIOS_SERVICE_URL}/auth/me"
    try:
        with httpx.Client(timeout=UPSTREAM_TIMEOUT_SECONDS) as client:
            response = client.get(url, headers={"Authorization": authorization})
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo validar usuario contra usuarios-service: {exc}",
        ) from exc

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    if response.status_code >= status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error validando token en usuarios-service ({response.status_code})",
        )

    payload = response.json()
    if not isinstance(payload, dict) or payload.get("rol") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol ADMIN",
        )
    return payload

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

database_url = _required_env('DATABASE_URL')
aula_repo = AulaRepositoryImpl(database_url)
aula_service = AulaService(aula_repo)

class AulaCreate(BaseModel):
    nombre: str
    capacidad: int

class AulaUpdate(BaseModel):
    nombre: str
    capacidad: int

class AulaResponse(BaseModel):
    id: int
    nombre: str
    capacidad: int

@app.get('/aulas', response_model=list[AulaResponse])
def get_aulas():
    aulas = aula_service.get_all_aulas()
    return [AulaResponse(id=a.id, nombre=a.nombre, capacidad=a.capacidad) for a in aulas]

@app.get('/aulas/{aula_id}', response_model=AulaResponse)
def get_aula(aula_id: int):
    aula = aula_service.get_aula_by_id(aula_id)
    if not aula:
        raise HTTPException(status_code=404, detail='Aula not found')
    return AulaResponse(id=aula.id, nombre=aula.nombre, capacidad=aula.capacidad)

@app.post('/aulas', response_model=AulaResponse, status_code=201)
def create_aula(aula: AulaCreate, _current_user: dict = Depends(_require_admin)):
    new_aula = aula_service.create_aula(aula.nombre, aula.capacidad)
    return AulaResponse(id=new_aula.id, nombre=new_aula.nombre, capacidad=new_aula.capacidad)

@app.put('/aulas/{aula_id}')
def update_aula(aula_id: int, aula: AulaUpdate, _current_user: dict = Depends(_require_admin)):
    updated = aula_service.update_aula(aula_id, aula.nombre, aula.capacidad)
    if not updated:
        raise HTTPException(status_code=404, detail='Aula not found')
    return {'message': 'Aula updated'}

@app.delete('/aulas/{aula_id}')
def delete_aula(aula_id: int, _current_user: dict = Depends(_require_admin)):
    deleted = aula_service.delete_aula(aula_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Aula not found')
    return {'message': 'Aula deleted'}


@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'aulas-service'}
