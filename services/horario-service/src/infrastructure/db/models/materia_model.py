from sqlalchemy import Column, Integer, String

from src.infrastructure.db.base import Base


class MateriaModel(Base):
	__tablename__ = "materias"

	id = Column(Integer, primary_key=True, index=True)
	nombre = Column(String, nullable=False)

