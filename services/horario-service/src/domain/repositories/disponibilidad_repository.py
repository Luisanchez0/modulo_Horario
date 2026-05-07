from abc import ABC, abstractmethod
from typing import List
from src.domain.models.disponibilidad import Disponibilidad

class DisponibilidadRepository(ABC):

    @abstractmethod
    def crear(self, disponibilidad: Disponibilidad) -> Disponibilidad:
        pass

    @abstractmethod
    def obtener_por_docente(self, docente_id: int) -> List[Disponibilidad]:
        pass