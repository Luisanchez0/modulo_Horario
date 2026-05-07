from abc import ABC, abstractmethod
from typing import List
from src.domain.models.materia import Materia

class MateriaRepository(ABC):

    @abstractmethod
    def crear(self, materia: Materia) -> Materia:
        pass

    @abstractmethod
    def listar(self) -> List[Materia]:
        pass