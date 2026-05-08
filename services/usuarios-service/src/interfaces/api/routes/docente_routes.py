from typing import List
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.repositories.docente_repository_impl import DocenteRepositoryImpl
from src.application.use_cases.create_docente import CreateDocente
from src.infrastructure.security.hash import hash as hash_password
from src.infrastructure.security.jwt import verify_token
from src.interfaces.api.schemas.docente_schema import DocenteCreate, DocenteResponse, DocenteUpdate

router = APIRouter()
repo = DocenteRepositoryImpl()
security = HTTPBearer()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _serialize_docente(docente: dict | object) -> dict[str, object]:
    if isinstance(docente, dict):
        return {
            "id": docente["id"],
            "matricula": docente.get("matricula"),
            "nombre": docente["nombre"],
            "correo": docente.get("correo"),
            "rol": docente.get("rol") or "DOCENTE",
            "turno": docente.get("turno") or "AMBOS",
            "estado": docente.get("estado") if docente.get("estado") is not None else True,
        }

    return {
        "id": docente.id,
        "matricula": docente.matricula,
        "nombre": docente.nombre,
        "correo": docente.correo,
        "rol": docente.rol or "DOCENTE",
        "turno": docente.turno or "AMBOS",
        "estado": docente.estado if docente.estado is not None else True,
    }


INTERNAL_API_KEY = _required_env("INTERNAL_API_KEY")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return payload


@router.get("/docentes", response_model=List[DocenteResponse])
def get_docentes(current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") == "ADMIN":
        return [_serialize_docente(docente) for docente in repo.get_all()]

    user_id = current_user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: usuario sin id",
        )

    docente = repo.find_by_id(int(user_id))
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente no encontrado",
        )
    return [_serialize_docente(docente)]


@router.get("/internal/docentes/{docente_id}")
def get_docente_internal(
    docente_id: int,
    x_internal_key: str = Header(default="", alias="X-Internal-Key"),
):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso interno no autorizado",
        )

    docente = repo.find_by_id(docente_id)
    if not docente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

    return _serialize_docente(docente)


@router.get("/internal/docentes")
def get_docentes_internal(
    x_internal_key: str = Header(default="", alias="X-Internal-Key"),
):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso interno no autorizado",
        )

    docentes = repo.get_all()
    return [_serialize_docente(docente) for docente in docentes]


@router.post("/docentes", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
def create_docente_admin(
    data: DocenteCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")

    use_case = CreateDocente(repo, hash_password)
    try:
        return use_case.execute(data.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put("/docentes/{docente_id}", response_model=DocenteResponse)
def update_docente_admin(
    docente_id: int,
    data: DocenteUpdate,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")

    payload = data.model_dump(exclude_unset=True)
    if payload.get("password"):
        payload["password"] = hash_password(payload["password"])

    updated = repo.update(docente_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

    return _serialize_docente(updated)


@router.delete("/docentes/{docente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_docente_admin(
    docente_id: int,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")

    deleted = repo.delete(docente_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")
