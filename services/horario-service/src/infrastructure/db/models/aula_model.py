from sqlalchemy import Column, Integer, String

from src.infrastructure.db.base import Base


class AulaModel(Base):
	__tablename__ = "aulas"

	id = Column(Integer, primary_key=True, index=True)
	nombre = Column(String, nullable=False)
	capacidad = Column(Integer, nullable=False)

