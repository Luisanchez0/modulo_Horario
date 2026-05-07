from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.application.use_cases.horario.crear_horario import CrearHorario
from src.application.use_cases.horario.generar_horarios import GenerarHorarios
from src.domain.models.horario import Horario
from src.domain.services.validaciones import HorarioDomainService
from src.infrastructure.repositories.disponibilidad_repository_impl import DisponibilidadRepositoryImpl
from src.infrastructure.repositories.horario_repository_impl import HorarioRepositoryImpl
from src.infrastructure.repositories.periodo_repository_impl import PeriodoRepositoryImpl
from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError
from fastapi import Header
from src.interfaces.api.schemas.horario_schema import (
    GenerarHorariosRequest,
    GenerarHorariosResponse,
    HorarioCreate,
    HorarioRead,
)

router = APIRouter(prefix="/horarios", tags=["Horarios"])


def _repo() -> HorarioRepositoryImpl:
    return HorarioRepositoryImpl()


def _catalog_client() -> CatalogServicesClient:
    return CatalogServicesClient()


def _to_horario_read(horario: Horario, *, strict_upstream: bool = False) -> HorarioRead:
    payload = vars(horario).copy()
    try:
        payload.update(
            _catalog_client().get_horario_labels(
                docente_id=horario.docente_id,
                materia_id=horario.materia_id,
                aula_id=horario.aula_id,
            )
        )
    except UpstreamServiceError as exc:
        if strict_upstream:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    return HorarioRead.model_validate(payload)


def _raise_if_missing_dependencies(docente_ids: list[int], materia_ids: list[int], aula_ids: list[int]) -> None:
    try:
        client = _catalog_client()
        missing_docentes = client.missing_docentes(docente_ids)
        missing_materias = client.missing_materias(materia_ids)
        missing_aulas = client.missing_aulas(aula_ids)
    except UpstreamServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    if missing_docentes or missing_materias or missing_aulas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Dependencias externas no encontradas",
                "docentes": missing_docentes,
                "materias": missing_materias,
                "aulas": missing_aulas,
            },
        )


def _generador() -> GenerarHorarios:
    return GenerarHorarios(
        horario_repo=HorarioRepositoryImpl(),
        disponibilidad_repo=DisponibilidadRepositoryImpl(),
        periodo_repo=PeriodoRepositoryImpl(),
        catalog_client=_catalog_client(),
    )


def _ensure_period_exists(periodo_id: int) -> None:
    try:
        PeriodoRepositoryImpl().obtener_por_id(periodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _validate_turnos_for_horario(payload: HorarioCreate) -> None:
    client = _catalog_client()
    try:
        docente = client.get_docente(payload.docente_id) or {}
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    try:
        HorarioDomainService.validar_horario_en_turno(
            payload.hora_inicio,
            payload.hora_fin,
            docente.get("turno"),
            "el docente",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _require_admin(authorization: str | None) -> None:
    try:
        current = _catalog_client().get_current_user(authorization)
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if not current or current.get("rol") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")


@router.post("", response_model=HorarioRead, status_code=status.HTTP_201_CREATED)
def crear_horario(payload: HorarioCreate, authorization: str | None = Header(None, alias="Authorization")) -> HorarioRead:
    _require_admin(authorization)
    _raise_if_missing_dependencies(
        docente_ids=[payload.docente_id],
        materia_ids=[payload.materia_id],
        aula_ids=[payload.aula_id],
    )
    _ensure_period_exists(payload.periodo_id)
    _validate_turnos_for_horario(payload)
    nuevo_horario = Horario(
        id=payload.id,
        docente_id=payload.docente_id,
        materia_id=payload.materia_id,
        aula_id=payload.aula_id,
        periodo_id=payload.periodo_id,
        dia=payload.dia,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
    )
    try:
        horario = CrearHorario(_repo()).ejecutar(nuevo_horario)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al crear horario: id {payload.id} ya existe",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_horario_read(horario, strict_upstream=True)


@router.get("", response_model=list[HorarioRead])
def listar_horarios() -> list[HorarioRead]:
    return [_to_horario_read(horario) for horario in _repo().listar()]


@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_horario(horario_id: int, authorization: str | None = Header(None, alias="Authorization")) -> None:
    _require_admin(authorization)
    try:
        _repo().eliminar(horario_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{horario_id}", response_model=HorarioRead, status_code=status.HTTP_200_OK)
def actualizar_horario(horario_id: int, payload: HorarioCreate, authorization: str | None = Header(None, alias="Authorization")) -> HorarioRead:
    _require_admin(authorization)
    _raise_if_missing_dependencies(
        docente_ids=[payload.docente_id],
        materia_ids=[payload.materia_id],
        aula_ids=[payload.aula_id],
    )
    _ensure_period_exists(payload.periodo_id)
    _validate_turnos_for_horario(payload)
    horario_actualizado = Horario(
        id=horario_id,
        docente_id=payload.docente_id,
        materia_id=payload.materia_id,
        aula_id=payload.aula_id,
        periodo_id=payload.periodo_id,
        dia=payload.dia,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
    )
    try:
        horario = _repo().actualizar(horario_id, horario_actualizado)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al actualizar horario: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_horario_read(horario, strict_upstream=True)


@router.post("/generar", response_model=GenerarHorariosResponse)
def generar_horarios(payload: GenerarHorariosRequest, authorization: str | None = Header(None, alias="Authorization")) -> GenerarHorariosResponse:
    _require_admin(authorization)
    if payload.docente_ids:
        docente_ids = payload.docente_ids
    else:
        try:
            docente_ids = [
                int(docente["id"])
                for docente in _catalog_client().list_docentes()
                if "id" in docente
            ]
        except UpstreamServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    if payload.materia_ids:
        materia_ids = payload.materia_ids
    else:
        try:
            materia_ids = [
                int(materia["id"])
                for materia in _catalog_client().list_materias()
                if "id" in materia
            ]
        except UpstreamServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    if payload.aula_ids:
        aula_ids = payload.aula_ids
    else:
        try:
            aula_ids = [
                int(aula["id"])
                for aula in _catalog_client().list_aulas()
                if "id" in aula
            ]
        except UpstreamServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    _raise_if_missing_dependencies(
        docente_ids=docente_ids,
        materia_ids=materia_ids,
        aula_ids=aula_ids,
    )

    try:
        creados, materias_sin_asignar, mensajes = _generador().ejecutar(
            periodo_id=payload.periodo_id,
            duracion_minutos=payload.duracion_minutos,
            hora_inicio_jornada=payload.hora_inicio_jornada,
            hora_fin_jornada=payload.hora_fin_jornada,
            dias=payload.dias,
            docente_ids=docente_ids,
            materia_ids=materia_ids,
            aula_ids=aula_ids,
        )
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "Periodo" in str(exc) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return GenerarHorariosResponse(
        periodo_id=payload.periodo_id,
        creados=[_to_horario_read(horario) for horario in creados],
        materias_sin_asignar=materias_sin_asignar,
        mensajes=mensajes,
    )
