import os
from typing import List
import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.materia import Materia
from app.domain.use_cases.materia_use_cases import MateriaUseCases, NoOpPublisher
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.sqlalchemy_materia_repository import (
    SQLAlchemyMateriaRepository,
)
from app.interfaces.schemas.materia_schema import (
    MateriaCreateRequest,
    MateriaResponse,
    MateriaUpdateRequest,
)

router = APIRouter(prefix="/materias", tags=["Materias"])
USUARIOS_SERVICE_URL = os.getenv("USUARIOS_SERVICE_URL", "http://localhost:8001")
UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5"))


def get_use_cases(db: AsyncSession = Depends(get_db)) -> MateriaUseCases:
    repo = SQLAlchemyMateriaRepository(db)
    return MateriaUseCases(repository=repo, publisher=NoOpPublisher())


async def _require_admin(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")

    url = f"{USUARIOS_SERVICE_URL}/auth/me"
    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers={"Authorization": authorization})
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


@router.post("/", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    payload: MateriaCreateRequest,
    _current_user: dict = Depends(_require_admin),
    use_cases: MateriaUseCases = Depends(get_use_cases),
):
    materia = Materia(
        nombre=payload.nombre,
        codigo=payload.codigo,
        creditos=payload.creditos,
        turno=payload.turno,
        descripcion=payload.descripcion,
    )
    created = await use_cases.create_materia(materia)
    return MateriaResponse(
        id=created.id,
        nombre=created.nombre,
        codigo=created.codigo,
        creditos=created.creditos,
        turno=created.turno,
        descripcion=created.descripcion,
    )


@router.get("/", response_model=List[MateriaResponse])
async def list_materias(use_cases: MateriaUseCases = Depends(get_use_cases)):
    materias = await use_cases.get_all_materias()
    return [
        MateriaResponse(
            id=m.id,
            nombre=m.nombre,
            codigo=m.codigo,
            creditos=m.creditos,
            turno=m.turno,
            descripcion=m.descripcion,
        )
        for m in materias
    ]


@router.get("/{materia_id}", response_model=MateriaResponse)
async def get_materia(
    materia_id: int,
    use_cases: MateriaUseCases = Depends(get_use_cases),
):
    materia = await use_cases.get_materia(materia_id)
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return MateriaResponse(
        id=materia.id,
        nombre=materia.nombre,
        codigo=materia.codigo,
        creditos=materia.creditos,
        turno=materia.turno,
        descripcion=materia.descripcion,
    )


@router.put("/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: int,
    payload: MateriaUpdateRequest,
    _current_user: dict = Depends(_require_admin),
    use_cases: MateriaUseCases = Depends(get_use_cases),
):
    existing = await use_cases.get_materia(materia_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    updated_entity = Materia(
        id=materia_id,
        nombre=payload.nombre or existing.nombre,
        codigo=payload.codigo or existing.codigo,
        creditos=payload.creditos or existing.creditos,
        turno=payload.turno or existing.turno,
        descripcion=payload.descripcion if payload.descripcion is not None else existing.descripcion,
    )
    updated = await use_cases.update_materia(updated_entity)
    return MateriaResponse(
        id=updated.id,
        nombre=updated.nombre,
        codigo=updated.codigo,
        creditos=updated.creditos,
        turno=updated.turno,
        descripcion=updated.descripcion,
    )


@router.delete("/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: int,
    _current_user: dict = Depends(_require_admin),
    use_cases: MateriaUseCases = Depends(get_use_cases),
):
    deleted = await use_cases.delete_materia(materia_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
