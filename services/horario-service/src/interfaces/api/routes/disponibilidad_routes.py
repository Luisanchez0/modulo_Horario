from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.application.use_cases.disponibilidad.crear_disponibilidad import CrearDisponibilidad
from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError
from src.infrastructure.repositories.disponibilidad_repository_impl import DisponibilidadRepositoryImpl
from src.interfaces.api.schemas.disponibilidad_schema import DisponibilidadCreate, DisponibilidadRead

router = APIRouter(prefix="/disponibilidades", tags=["Disponibilidades"])


def _repo() -> DisponibilidadRepositoryImpl:
    return DisponibilidadRepositoryImpl()


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


@router.post("", response_model=DisponibilidadRead, status_code=status.HTTP_201_CREATED)
def crear_disponibilidad(payload: DisponibilidadCreate) -> DisponibilidadRead:
    try:
        docente = _catalog_client().get_docente(payload.docente_id)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if docente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente {payload.docente_id} no encontrado",
        )

    try:
        disponibilidad = CrearDisponibilidad(_repo()).ejecutar(
            payload.id,
            payload.docente_id,
            payload.dia,
            payload.hora_inicio,
            payload.hora_fin,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al crear disponibilidad: id {payload.id} ya existe",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return DisponibilidadRead.model_validate(vars(disponibilidad))


@router.get("/docente/{docente_id}", response_model=list[DisponibilidadRead])
def listar_por_docente(docente_id: int) -> list[DisponibilidadRead]:
    return [
        DisponibilidadRead.model_validate(vars(disponibilidad))
        for disponibilidad in _repo().obtener_por_docente(docente_id)
    ]
