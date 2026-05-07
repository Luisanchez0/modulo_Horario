from abc import ABC, abstractmethod
from typing import List
from src.domain.models.horario import Horario

class HorarioRepository(ABC):

    @abstractmethod
    def crear(self, horario: Horario) -> Horario:
        pass

    @abstractmethod
    def listar(self) -> List[Horario]:
        pass

    @abstractmethod
    def obtener_por_docente_y_periodo(
        self, docente_id: int, periodo_id: int
    ) -> List[Horario]:
        pass

    @abstractmethod
    def obtener_por_aula_y_periodo(
        self, aula_id: int, periodo_id: int
    ) -> List[Horario]:
        pass

    @abstractmethod
    def actualizar(self, horario_id: int, horario: Horario) -> Horario:
        pass