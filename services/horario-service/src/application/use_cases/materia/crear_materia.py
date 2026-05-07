from src.domain.models.materia import Materia
from src.domain.repositories.materia_repository import MateriaRepository


class CrearMateria:

    def __init__(self, repo: MateriaRepository):
        self.repo = repo

    def ejecutar(self, id: int, nombre: str):
        materia = Materia(id=id, nombre=nombre)
        return self.repo.crear(materia)