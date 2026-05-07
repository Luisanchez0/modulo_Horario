from src.domain.models.docente import Docente
from src.domain.repositories.docente_repository import DocenteRepository
from src.infrastructure.db.models.docente_model import DocenteModel
from src.infrastructure.db.session import SessionLocal


class DocenteRepositoryImpl(DocenteRepository):
    def crear(self, docente: Docente) -> Docente:
        session = SessionLocal()
        try:
            entity = DocenteModel(id=docente.id, nombre=docente.nombre)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return Docente(id=getattr(entity, "id"), nombre=getattr(entity, "nombre"))
        finally:
            session.close()

    def obtener_por_id(self, docente_id: int) -> Docente:
        session = SessionLocal()
        try:
            entity = session.get(DocenteModel, docente_id)
            if entity is None:
                raise ValueError(f"Docente {docente_id} no encontrado")
            return Docente(id=getattr(entity, "id"), nombre=getattr(entity, "nombre"))
        finally:
            session.close()

    def listar(self) -> list[Docente]:
        session = SessionLocal()
        try:
            return [
                Docente(id=getattr(item, "id"), nombre=getattr(item, "nombre"))
                for item in session.query(DocenteModel).order_by(DocenteModel.id).all()
            ]
        finally:
            session.close()
