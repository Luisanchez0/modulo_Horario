from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.domain.repository.aula_repository import AulaRepository
from src.core.domain.entity.aula import Aula

Base = declarative_base()

class AulaModel(Base):
    __tablename__ = 'aulas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    capacidad = Column(Integer, nullable=False)

class AulaRepositoryImpl(AulaRepository):
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all(self) -> list[Aula]:
        session = self.Session()
        try:
            models = session.query(AulaModel).all()
            return [Aula(id=m.id, nombre=m.nombre, capacidad=m.capacidad) for m in models]
        finally:
            session.close()

    def get_by_id(self, id: int) -> Aula:
        session = self.Session()
        try:
            model = session.query(AulaModel).filter(AulaModel.id == id).first()
            if model:
                return Aula(id=model.id, nombre=model.nombre, capacidad=model.capacidad)
            return None
        finally:
            session.close()

    def save(self, aula: Aula) -> None:
        session = self.Session()
        try:
            model = AulaModel(nombre=aula.nombre, capacidad=aula.capacidad)
            session.add(model)
            session.commit()
            aula.id = model.id  # Set the id back
        finally:
            session.close()

    def update(self, aula: Aula) -> bool:
        session = self.Session()
        try:
            model = session.query(AulaModel).filter(AulaModel.id == aula.id).first()
            if not model:
                return False
            model.nombre = aula.nombre
            model.capacidad = aula.capacidad
            session.commit()
            return True
        finally:
            session.close()

    def delete(self, id: int) -> bool:
        session = self.Session()
        try:
            model = session.query(AulaModel).filter(AulaModel.id == id).first()
            if not model:
                return False
            session.delete(model)
            session.commit()
            return True
        finally:
            session.close()
