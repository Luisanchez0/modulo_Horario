from src.domain.models.periodo import Periodo
from src.domain.repositories.periodo_repository import PeriodoRepository


class CrearPeriodo:

    def __init__(self, repo: PeriodoRepository):
        self.repo = repo

    def ejecutar(self, id: int | None, nombre: str, tipo: str, fecha_inicio: str, fecha_fin: str):

        if tipo not in ["SEMESTRE", "CUATRIMESTRE"]:
            raise ValueError("Tipo de periodo inválido")

        periodo = Periodo(
            id=id,
            nombre=nombre,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        return self.repo.crear(periodo)
