from src.domain.models.horario import Horario
from src.domain.repositories.horario_repository import HorarioRepository
from src.infrastructure.db.models.horario_model import HorarioModel
from src.infrastructure.db.session import SessionLocal


class HorarioRepositoryImpl(HorarioRepository):
    def crear(self, horario: Horario) -> Horario:
        session = SessionLocal()
        try:
            values = dict(
                docente_id=horario.docente_id,
                materia_id=horario.materia_id,
                aula_id=horario.aula_id,
                periodo_id=horario.periodo_id,
                dia=horario.dia,
                hora_inicio=horario.hora_inicio,
                hora_fin=horario.hora_fin,
            )
            if horario.id is not None:
                values["id"] = horario.id
            entity = HorarioModel(**values)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return Horario(
                id=getattr(entity, "id"),
                docente_id=getattr(entity, "docente_id"),
                materia_id=getattr(entity, "materia_id"),
                aula_id=getattr(entity, "aula_id"),
                periodo_id=getattr(entity, "periodo_id"),
                dia=getattr(entity, "dia"),
                hora_inicio=getattr(entity, "hora_inicio"),
                hora_fin=getattr(entity, "hora_fin"),
            )
        finally:
            session.close()

    def listar(self) -> list[Horario]:
        session = SessionLocal()
        try:
            return [
                Horario(
                    id=getattr(item, "id"),
                    docente_id=getattr(item, "docente_id"),
                    materia_id=getattr(item, "materia_id"),
                    aula_id=getattr(item, "aula_id"),
                    periodo_id=getattr(item, "periodo_id"),
                    dia=getattr(item, "dia"),
                    hora_inicio=getattr(item, "hora_inicio"),
                    hora_fin=getattr(item, "hora_fin"),
                )
                for item in session.query(HorarioModel).order_by(HorarioModel.id).all()
            ]
        finally:
            session.close()

    def obtener_por_docente_y_periodo(self, docente_id: int, periodo_id: int) -> list[Horario]:
        session = SessionLocal()
        try:
            return [
                Horario(
                    id=getattr(item, "id"),
                    docente_id=getattr(item, "docente_id"),
                    materia_id=getattr(item, "materia_id"),
                    aula_id=getattr(item, "aula_id"),
                    periodo_id=getattr(item, "periodo_id"),
                    dia=getattr(item, "dia"),
                    hora_inicio=getattr(item, "hora_inicio"),
                    hora_fin=getattr(item, "hora_fin"),
                )
                for item in session.query(HorarioModel)
                .filter(HorarioModel.docente_id == docente_id)
                .filter(HorarioModel.periodo_id == periodo_id)
                .order_by(HorarioModel.id)
                .all()
            ]
        finally:
            session.close()

    def obtener_por_aula_y_periodo(self, aula_id: int, periodo_id: int) -> list[Horario]:
        session = SessionLocal()
        try:
            return [
                Horario(
                    id=getattr(item, "id"),
                    docente_id=getattr(item, "docente_id"),
                    materia_id=getattr(item, "materia_id"),
                    aula_id=getattr(item, "aula_id"),
                    periodo_id=getattr(item, "periodo_id"),
                    dia=getattr(item, "dia"),
                    hora_inicio=getattr(item, "hora_inicio"),
                    hora_fin=getattr(item, "hora_fin"),
                )
                for item in session.query(HorarioModel)
                .filter(HorarioModel.aula_id == aula_id)
                .filter(HorarioModel.periodo_id == periodo_id)
                .order_by(HorarioModel.id)
                .all()
            ]
        finally:
            session.close()

    def listar_por_periodo(self, periodo_id: int) -> list[dict]:
        session = SessionLocal()
        try:
            rows = (
                session.query(HorarioModel)
                .filter(HorarioModel.periodo_id == periodo_id)
                .order_by(HorarioModel.id)
                .all()
            )
            return [
                {
                    "id": getattr(r, "id"),
                    "docente_id": getattr(r, "docente_id"),
                    "materia_id": getattr(r, "materia_id"),
                    "aula_id": getattr(r, "aula_id"),
                    "dia": getattr(r, "dia"),
                    "hora_inicio": getattr(r, "hora_inicio"),
                    "hora_fin": getattr(r, "hora_fin"),
                }
                for r in rows
            ]
        finally:
            session.close()

    def eliminar(self, horario_id: int) -> None:
        session = SessionLocal()
        try:
            entity = session.get(HorarioModel, horario_id)
            if entity is None:
                raise ValueError(f"Horario {horario_id} no encontrado")
            session.delete(entity)
            session.commit()
        finally:
            session.close()

    def actualizar(self, horario_id: int, horario: Horario) -> Horario:
        session = SessionLocal()
        try:
            entity = session.get(HorarioModel, horario_id)
            if entity is None:
                raise ValueError(f"Horario {horario_id} no encontrado")
            entity.docente_id = horario.docente_id
            entity.materia_id = horario.materia_id
            entity.aula_id = horario.aula_id
            entity.periodo_id = horario.periodo_id
            entity.dia = horario.dia
            entity.hora_inicio = horario.hora_inicio
            entity.hora_fin = horario.hora_fin
            session.commit()
            session.refresh(entity)
            return Horario(
                id=getattr(entity, "id"),
                docente_id=getattr(entity, "docente_id"),
                materia_id=getattr(entity, "materia_id"),
                aula_id=getattr(entity, "aula_id"),
                periodo_id=getattr(entity, "periodo_id"),
                dia=getattr(entity, "dia"),
                hora_inicio=getattr(entity, "hora_inicio"),
                hora_fin=getattr(entity, "hora_fin"),
            )
        finally:
            session.close()
