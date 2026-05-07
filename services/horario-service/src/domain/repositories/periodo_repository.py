from abc import ABC, abstractmethod
from typing import List
from src.domain.models.periodo import Periodo

class PeriodoRepository(ABC):

    @abstractmethod
    def crear(self, periodo: Periodo) -> Periodo:
        pass

    @abstractmethod
    def obtener_por_id(self, periodo_id: int) -> Periodo:
        pass

    @abstractmethod
    def listar(self) -> List[Periodo]:
        pass