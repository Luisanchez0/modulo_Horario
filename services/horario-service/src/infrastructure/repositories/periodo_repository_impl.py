from sqlalchemy import func

from src.domain.models.periodo import Periodo
from src.domain.repositories.periodo_repository import PeriodoRepository
from src.infrastructure.db.models.periodo_model import PeriodoModel
from src.infrastructure.db.session import SessionLocal


class PeriodoRepositoryImpl(PeriodoRepository):
    def crear(self, periodo: Periodo) -> Periodo:
        session = SessionLocal()
        try:
            periodo_id = periodo.id
            if periodo_id is None:
                periodo_id = (session.query(func.max(PeriodoModel.id)).scalar() or 0) + 1
            entity = PeriodoModel(
                id=periodo_id,
                nombre=periodo.nombre,
                tipo=periodo.tipo,
                fecha_inicio=periodo.fecha_inicio,
                fecha_fin=periodo.fecha_fin,
            )
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return Periodo(
                id=getattr(entity, "id"),
                nombre=getattr(entity, "nombre"),
                tipo=getattr(entity, "tipo"),
                fecha_inicio=getattr(entity, "fecha_inicio"),
                fecha_fin=getattr(entity, "fecha_fin"),
            )
        finally:
            session.close()

    def obtener_por_id(self, periodo_id: int) -> Periodo:
        session = SessionLocal()
        try:
            entity = session.get(PeriodoModel, periodo_id)
            if entity is None:
                raise ValueError(f"Periodo {periodo_id} no encontrado")
            return Periodo(
                id=getattr(entity, "id"),
                nombre=getattr(entity, "nombre"),
                tipo=getattr(entity, "tipo"),
                fecha_inicio=getattr(entity, "fecha_inicio"),
                fecha_fin=getattr(entity, "fecha_fin"),
            )
        finally:
            session.close()

    def listar(self) -> list[Periodo]:
        session = SessionLocal()
        try:
            return [
                Periodo(
                    id=getattr(item, "id"),
                    nombre=getattr(item, "nombre"),
                    tipo=getattr(item, "tipo"),
                    fecha_inicio=getattr(item, "fecha_inicio"),
                    fecha_fin=getattr(item, "fecha_fin"),
                )
                for item in session.query(PeriodoModel).order_by(PeriodoModel.id).all()
            ]
        finally:
            session.close()

    def eliminar(self, periodo_id: int) -> None:
        session = SessionLocal()
        try:
            entity = session.get(PeriodoModel, periodo_id)
            if entity is None:
                raise ValueError(f"Periodo {periodo_id} no encontrado")
            session.delete(entity)
            try:
                session.commit()
            except Exception:
                session.rollback()
                # Convert DB integrity errors into a runtime error
                raise RuntimeError("Periodo tiene dependencias y no puede eliminarse")
        finally:
            session.close()
