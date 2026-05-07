from src.domain.models.docente import Docente
from src.domain.repositories.docente_repository import DocenteRepository


class CrearDocente:

    def __init__(self, repo: DocenteRepository):
        self.repo = repo

    def ejecutar(self, id: int, nombre: str):
        docente = Docente(id=id, nombre=nombre)
        return self.repo.crear(docente)