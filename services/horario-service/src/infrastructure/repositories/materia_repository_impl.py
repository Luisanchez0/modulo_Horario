from src.domain.models.materia import Materia
from src.domain.repositories.materia_repository import MateriaRepository
from src.infrastructure.db.models.materia_model import MateriaModel
from src.infrastructure.db.session import SessionLocal


class MateriaRepositoryImpl(MateriaRepository):
    def crear(self, materia: Materia) -> Materia:
        session = SessionLocal()
        try:
            entity = MateriaModel(id=materia.id, nombre=materia.nombre)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return Materia(id=getattr(entity, "id"), nombre=getattr(entity, "nombre"))
        finally:
            session.close()

    def listar(self) -> list[Materia]:
        session = SessionLocal()
        try:
            return [
                Materia(id=getattr(item, "id"), nombre=getattr(item, "nombre"))
                for item in session.query(MateriaModel).order_by(MateriaModel.id).all()
            ]
        finally:
            session.close()
