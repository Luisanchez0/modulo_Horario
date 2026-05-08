from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.entities.materia import Materia
from app.domain.ports.materia_repository_port import MateriaRepositoryPort
from app.infrastructure.db.models import MateriaModel


class SQLAlchemyMateriaRepository(MateriaRepositoryPort):

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: MateriaModel) -> Materia:
        return Materia(
            id=model.id,
            nombre=model.nombre,
            codigo=model.codigo,
            creditos=model.creditos,
            turno=model.turno or "AMBOS",
            descripcion=model.descripcion,
        )

    def _to_model(self, entity: Materia) -> MateriaModel:
        return MateriaModel(
            id=entity.id,
            nombre=entity.nombre,
            codigo=entity.codigo,
            creditos=entity.creditos,
            turno=entity.turno,
            descripcion=entity.descripcion,
        )

    async def create(self, materia: Materia) -> Materia:
        model = MateriaModel(
            nombre=materia.nombre,
            codigo=materia.codigo,
            creditos=materia.creditos,
            turno=materia.turno,
            descripcion=materia.descripcion,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, materia_id: int) -> Optional[Materia]:
        result = await self._session.execute(
            select(MateriaModel).where(MateriaModel.id == materia_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[Materia]:
        result = await self._session.execute(select(MateriaModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, materia: Materia) -> Optional[Materia]:
        result = await self._session.execute(
            select(MateriaModel).where(MateriaModel.id == materia.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.nombre = materia.nombre
        model.codigo = materia.codigo
        model.creditos = materia.creditos
        model.turno = materia.turno
        model.descripcion = materia.descripcion
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, materia_id: int) -> bool:
        result = await self._session.execute(
            select(MateriaModel).where(MateriaModel.id == materia_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
