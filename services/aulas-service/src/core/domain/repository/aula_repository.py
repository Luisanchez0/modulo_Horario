from abc import ABC, abstractmethod
from src.core.domain.entity.aula import Aula

class AulaRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Aula]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Aula:
        pass

    @abstractmethod
    def save(self, aula: Aula) -> None:
        pass

    @abstractmethod
    def update(self, aula: Aula) -> bool:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
