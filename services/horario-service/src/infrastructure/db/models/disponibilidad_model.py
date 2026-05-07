from sqlalchemy import Column, Integer, String, ForeignKey

from src.infrastructure.db.base import Base


class DisponibilidadModel(Base):
	__tablename__ = "disponibilidades"

	id = Column(Integer, primary_key=True, index=True)
	docente_id = Column(Integer, ForeignKey("docentes.id"), nullable=False)
	dia = Column(String, nullable=False)
	hora_inicio = Column(String, nullable=False)
	hora_fin = Column(String, nullable=False)

