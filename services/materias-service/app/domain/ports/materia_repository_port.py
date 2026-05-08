from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.materia import Materia


class MateriaRepositoryPort(ABC):

    @abstractmethod
    async def create(self, materia: Materia) -> Materia:
        pass

    @abstractmethod
    async def get_by_id(self, materia_id: int) -> Optional[Materia]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Materia]:
        pass

    @abstractmethod
    async def update(self, materia: Materia) -> Optional[Materia]:
        pass

    @abstractmethod
    async def delete(self, materia_id: int) -> bool:
        pass
