from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DocenteModel(Base):
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(50), unique=True, nullable=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    password = Column(String(255))
    rol = Column(String(50), default="DOCENTE", nullable=False)
    turno = Column(String(20), default="AMBOS", nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
