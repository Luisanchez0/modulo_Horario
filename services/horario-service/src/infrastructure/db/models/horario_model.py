from sqlalchemy import Column, Integer, String, ForeignKey

from src.infrastructure.db.base import Base


class HorarioModel(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    docente_id = Column(Integer, ForeignKey("docentes.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    aula_id = Column(Integer, ForeignKey("aulas.id"), nullable=False)
    periodo_id = Column(Integer, ForeignKey("periodos.id"), nullable=False)
    dia = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin = Column(String, nullable=False)
