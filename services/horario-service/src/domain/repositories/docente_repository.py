from abc import ABC, abstractmethod
from typing import List
from src.domain.models.docente import Docente

class DocenteRepository(ABC):

    @abstractmethod
    def crear(self, docente: Docente) -> Docente:
        pass

    @abstractmethod
    def obtener_por_id(self, docente_id: int) -> Docente:
        pass

    @abstractmethod
    def listar(self) -> List[Docente]:
        pass