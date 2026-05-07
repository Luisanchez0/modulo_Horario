from abc import ABC, abstractmethod
from typing import List
from src.domain.models.aula import Aula

class AulaRepository(ABC):

    @abstractmethod
    def crear(self, aula: Aula) -> Aula:
        pass

    @abstractmethod
    def listar(self) -> List[Aula]:
        pass