from src.core.domain.repository.aula_repository import AulaRepository
from src.core.domain.entity.aula import Aula

class AulaService:
    def __init__(self, aula_repository: AulaRepository):
        self.aula_repository = aula_repository

    def get_all_aulas(self) -> list[Aula]:
        return self.aula_repository.get_all()

    def get_aula_by_id(self, id: int) -> Aula:
        return self.aula_repository.get_by_id(id)

    def create_aula(self, nombre: str, capacidad: int) -> Aula:
        # Assume id is auto-generated, for simplicity
        aula = Aula(id=None, nombre=nombre, capacidad=capacidad)
        self.aula_repository.save(aula)
        return aula

    def update_aula(self, id: int, nombre: str, capacidad: int) -> bool:
        aula = Aula(id=id, nombre=nombre, capacidad=capacidad)
        return self.aula_repository.update(aula)

    def delete_aula(self, id: int) -> bool:
        return self.aula_repository.delete(id)
