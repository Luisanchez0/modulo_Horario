from src.domain.models.disponibilidad import Disponibilidad
from src.domain.repositories.disponibilidad_repository import DisponibilidadRepository
from src.infrastructure.db.models.disponibilidad_model import DisponibilidadModel
from src.infrastructure.db.session import SessionLocal


class DisponibilidadRepositoryImpl(DisponibilidadRepository):

	def crear(self, disponibilidad: Disponibilidad) -> Disponibilidad:
		session = SessionLocal()
		try:
			values = dict(
				docente_id=disponibilidad.docente_id,
				dia=disponibilidad.dia,
				hora_inicio=disponibilidad.hora_inicio,
				hora_fin=disponibilidad.hora_fin,
			)
			if disponibilidad.id is not None:
				values["id"] = disponibilidad.id
			entity = DisponibilidadModel(**values)
			session.add(entity)
			session.commit()
			session.refresh(entity)
			return Disponibilidad(
				id=getattr(entity, "id"),
				docente_id=getattr(entity, "docente_id"),
				dia=getattr(entity, "dia"),
				hora_inicio=getattr(entity, "hora_inicio"),
				hora_fin=getattr(entity, "hora_fin"),
			)
		finally:
			session.close()

	def obtener_por_docente(self, docente_id: int) -> list[Disponibilidad]:
		session = SessionLocal()
		try:
			return [
				Disponibilidad(
					id=getattr(item, "id"),
					docente_id=getattr(item, "docente_id"),
					dia=getattr(item, "dia"),
					hora_inicio=getattr(item, "hora_inicio"),
					hora_fin=getattr(item, "hora_fin"),
				)
				for item in session.query(DisponibilidadModel)
				.filter(DisponibilidadModel.docente_id == docente_id)
				.order_by(DisponibilidadModel.id)
				.all()
			]
		finally:
			session.close()
