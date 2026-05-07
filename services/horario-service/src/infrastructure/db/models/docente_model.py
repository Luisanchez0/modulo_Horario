from sqlalchemy import Column, Integer, String
from src.infrastructure.db.base import Base

class DocenteModel(Base):
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)