from typing import List, Optional
from app.domain.entities.materia import Materia
from app.domain.ports.materia_repository_port import MateriaRepositoryPort


class NoOpPublisher:
    async def publish(self, routing_key: str, message: dict) -> None:
        return


class MateriaUseCases:

    def __init__(
        self,
        repository: MateriaRepositoryPort,
        publisher: NoOpPublisher | None = None,
    ):
        self._repository = repository
        self._publisher = publisher or NoOpPublisher()

    async def create_materia(self, materia: Materia) -> Materia:
        created = await self._repository.create(materia)
        await self._publisher.publish(
            routing_key="materia.created",
            message={
                "event": "materia.created",
                "data": {
                    "id": created.id,
                    "nombre": created.nombre,
                    "codigo": created.codigo,
                    "creditos": created.creditos,
                    "turno": created.turno,
                    "descripcion": created.descripcion,
                },
            },
        )
        return created

    async def get_materia(self, materia_id: int) -> Optional[Materia]:
        return await self._repository.get_by_id(materia_id)

    async def get_all_materias(self) -> List[Materia]:
        return await self._repository.get_all()

    async def update_materia(self, materia: Materia) -> Optional[Materia]:
        updated = await self._repository.update(materia)
        if updated:
            await self._publisher.publish(
                routing_key="materia.updated",
                message={
                    "event": "materia.updated",
                    "data": {
                        "id": updated.id,
                        "nombre": updated.nombre,
                        "codigo": updated.codigo,
                        "creditos": updated.creditos,
                        "turno": updated.turno,
                        "descripcion": updated.descripcion,
                    },
                },
            )
        return updated

    async def delete_materia(self, materia_id: int) -> bool:
        deleted = await self._repository.delete(materia_id)
        if deleted:
            await self._publisher.publish(
                routing_key="materia.deleted",
                message={"event": "materia.deleted", "data": {"id": materia_id}},
            )
        return deleted
