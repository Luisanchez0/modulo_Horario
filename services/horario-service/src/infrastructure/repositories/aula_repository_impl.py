from src.domain.models.aula import Aula
from src.domain.repositories.aula_repository import AulaRepository
from src.infrastructure.db.models.aula_model import AulaModel
from src.infrastructure.db.session import SessionLocal


class AulaRepositoryImpl(AulaRepository):
    def crear(self, aula: Aula) -> Aula:
        session = SessionLocal()
        try:
            entity = AulaModel(
                id=aula.id,
                nombre=aula.nombre,
                capacidad=aula.capacidad,
            )
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return Aula(
                id=getattr(entity, "id"),
                nombre=getattr(entity, "nombre"),
                capacidad=getattr(entity, "capacidad"),
            )
        finally:
            session.close()

    def listar(self) -> list[Aula]:
        session = SessionLocal()
        try:
            return [
                Aula(
                    id=getattr(item, "id"),
                    nombre=getattr(item, "nombre"),
                    capacidad=getattr(item, "capacidad"),
                )
                for item in session.query(AulaModel).order_by(AulaModel.id).all()
            ]
        finally:
            session.close()
