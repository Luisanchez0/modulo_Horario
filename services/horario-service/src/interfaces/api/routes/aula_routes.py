from fastapi import APIRouter, HTTPException, status

from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError
from src.interfaces.api.schemas.aula_schema import AulaRead

router = APIRouter(prefix="/aulas", tags=["Aulas"])


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


@router.post("", response_model=AulaRead, status_code=status.HTTP_201_CREATED)
def crear_aula() -> AulaRead:
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Operacion no permitida: aulas se administra en aulas-service",
    )


@router.get("", response_model=list[AulaRead])
def listar_aulas() -> list[AulaRead]:
    try:
        aulas = _catalog_client().list_aulas()
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    respuesta: list[AulaRead] = []

    for item in aulas:
        aula_id = int(item.get("id"))
        nombre = str(item.get("nombre") or f"Aula {aula_id}")
        capacidad = int(item.get("capacidad") or 0)
        respuesta.append(AulaRead(id=aula_id, nombre=nombre, capacidad=capacidad))

    return respuesta
