from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MateriaModel(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), nullable=False, unique=True)
    creditos = Column(Integer, nullable=False)
    turno = Column(String(20), nullable=False, default="AMBOS")
    descripcion = Column(Text, nullable=True)
