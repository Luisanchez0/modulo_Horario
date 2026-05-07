from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi import Header
from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError

from src.application.use_cases.periodo.crear_periodo import CrearPeriodo
from src.infrastructure.repositories.periodo_repository_impl import PeriodoRepositoryImpl
from src.infrastructure.repositories.horario_repository_impl import HorarioRepositoryImpl
from src.interfaces.api.schemas.periodo_schema import PeriodoCreate, PeriodoRead

router = APIRouter(prefix="/periodos", tags=["Periodos"])


def _repo() -> PeriodoRepositoryImpl:
    return PeriodoRepositoryImpl()


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


@router.post("", response_model=PeriodoRead, status_code=status.HTTP_201_CREATED)
def crear_periodo(payload: PeriodoCreate, authorization: str | None = Header(None, alias="Authorization")) -> PeriodoRead:
    try:
        current = _catalog_client().get_current_user(authorization)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if not current or current.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")
    try:
        periodo = CrearPeriodo(_repo()).ejecutar(
            payload.id,
            payload.nombre,
            payload.tipo,
            payload.fecha_inicio,
            payload.fecha_fin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al crear periodo: id {payload.id} ya existe",
        ) from exc
    return PeriodoRead.model_validate(vars(periodo))


@router.get("", response_model=list[PeriodoRead])
def listar_periodos() -> list[PeriodoRead]:
    return [PeriodoRead.model_validate(vars(periodo)) for periodo in _repo().listar()]


@router.get("/{periodo_id}", response_model=PeriodoRead)
def obtener_periodo(periodo_id: int) -> PeriodoRead:
    try:
        periodo = _repo().obtener_por_id(periodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PeriodoRead.model_validate(vars(periodo))


@router.delete("/{periodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_periodo(periodo_id: int, authorization: str | None = Header(None, alias="Authorization")) -> None:
    try:
        current = _catalog_client().get_current_user(authorization)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if not current or current.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")
    # Check for dependent horarios before attempting delete
    dependencias = HorarioRepositoryImpl().listar_por_periodo(periodo_id)
    if dependencias:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "No se puede eliminar el periodo: existen horarios vinculados",
                "dependencias": dependencias,
            },
        )
    try:
        _repo().eliminar(periodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
