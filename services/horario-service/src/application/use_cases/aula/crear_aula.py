from src.domain.models.aula import Aula
from src.domain.repositories.aula_repository import AulaRepository


class CrearAula:

    def __init__(self, repo: AulaRepository):
        self.repo = repo

    def ejecutar(self, id: int, nombre: str, capacidad: int):
        aula = Aula(id=id, nombre=nombre, capacidad=capacidad)
        return self.repo.crear(aula)