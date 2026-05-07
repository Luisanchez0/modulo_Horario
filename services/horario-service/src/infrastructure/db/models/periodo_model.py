from sqlalchemy import Column, Integer, String

from src.infrastructure.db.base import Base


class PeriodoModel(Base):
    __tablename__ = "periodos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    fecha_inicio = Column(String, nullable=False)
    fecha_fin = Column(String, nullable=False)
