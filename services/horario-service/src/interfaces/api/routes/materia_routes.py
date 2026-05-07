from fastapi import APIRouter, HTTPException, status

from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError
from src.interfaces.api.schemas.materia_schema import MateriaRead

router = APIRouter(prefix="/materias", tags=["Materias"])


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


@router.post("", response_model=MateriaRead, status_code=status.HTTP_201_CREATED)
def crear_materia() -> MateriaRead:
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Operacion no permitida: materias se administra en materias-service",
    )


@router.get("", response_model=list[MateriaRead])
def listar_materias() -> list[MateriaRead]:
    try:
        materias = _catalog_client().list_materias()
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    respuesta: list[MateriaRead] = []

    for item in materias:
        materia_id_raw = item.get("id")
        if materia_id_raw is None:
            continue
        materia_id = int(materia_id_raw)
        nombre = str(item.get("nombre") or f"Materia {materia_id}")
        respuesta.append(MateriaRead(id=materia_id, nombre=nombre))

    return respuesta
