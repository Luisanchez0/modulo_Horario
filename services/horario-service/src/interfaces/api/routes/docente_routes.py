from fastapi import APIRouter, HTTPException, status

from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError
from src.interfaces.api.schemas.docente_schema import DocenteRead

router = APIRouter(prefix="/docentes", tags=["Docentes"])


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


@router.post("", response_model=DocenteRead, status_code=status.HTTP_201_CREATED)
def crear_docente() -> DocenteRead:
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Operacion no permitida: docentes se administra en usuarios-service",
    )


@router.get("", response_model=list[DocenteRead])
def listar_docentes() -> list[DocenteRead]:
    try:
        docentes = _catalog_client().list_docentes()
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    respuesta: list[DocenteRead] = []
    for item in docentes:
        docente_id_raw = item.get("id")
        if docente_id_raw is None:
            continue
        docente_id = int(docente_id_raw)
        nombre = str(item.get("nombre") or f"Docente {docente_id}")
        respuesta.append(DocenteRead(id=docente_id, nombre=nombre))

    return respuesta


@router.get("/{docente_id}", response_model=DocenteRead)
def obtener_docente(docente_id: int) -> DocenteRead:
    try:
        docente = _catalog_client().get_docente(docente_id)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente {docente_id} no encontrado",
        )
    return DocenteRead(
        id=docente_id,
        nombre=str(docente.get("nombre") or f"Docente {docente_id}"),
    )
