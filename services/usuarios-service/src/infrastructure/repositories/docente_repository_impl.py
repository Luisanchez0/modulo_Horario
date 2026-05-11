from src.application.ports.docente_repository import DocenteRepository
from src.infrastructure.db.models import DocenteModel
from src.infrastructure.db.connection import SessionLocal

class DocenteRepositoryImpl(DocenteRepository):

    @staticmethod
    def _normalizar_turno(value):
        turno = str(value or "AMBOS").strip().upper()
        if turno in {"MATUTINO", "VESPERTINO", "AMBOS"}:
            return turno
        return "AMBOS"

    def save(self, data):
        with SessionLocal() as db:
            data = dict(data)
            data["turno"] = self._normalizar_turno(data.get("turno"))
            data["matricula"] = data.get("matricula") or None
            docente = DocenteModel(**data)
            db.add(docente)
            db.commit()
            db.refresh(docente)
            return docente

    def find_by_email(self, correo):
        with SessionLocal() as db:
            return db.query(DocenteModel).filter_by(correo=correo).first()

    def obtener_por_correo(self, correo):
        return self.find_by_email(correo)

    def find_by_id(self, docente_id):
        with SessionLocal() as db:
            return db.query(DocenteModel).filter_by(id=docente_id).first()

    def get_all(self):
        with SessionLocal() as db:
            docentes = db.query(DocenteModel).all()
            # Serializar a dict mientras estamos en la sesión para mantener valores normalizados
            result = []
            for docente in docentes:
                result.append({
                    "id": docente.id,
                    "matricula": docente.matricula,
                    "nombre": docente.nombre,
                    "correo": docente.correo,
                    "rol": docente.rol or "DOCENTE",
                    "turno": docente.turno or "AMBOS",
                    "estado": docente.estado if docente.estado is not None else True
                })
            return result

    def update(self, docente_id, data):
        with SessionLocal() as db:
            docente = db.query(DocenteModel).filter_by(id=docente_id).first()
            if not docente:
                return None

            for field, value in data.items():
                if value is None:
                    continue
                if field == "role":
                    docente.rol = "ADMIN" if str(value).upper() == "ADMIN" else "DOCENTE"
                elif field == "turno":
                    docente.turno = self._normalizar_turno(value)
                elif field == "password":
                    docente.password = value
                elif field == "matricula":
                    docente.matricula = value or None
                elif hasattr(docente, field):
                    setattr(docente, field, value)

            db.commit()
            db.refresh(docente)
            return docente

    def delete(self, docente_id):
        with SessionLocal() as db:
            docente = db.query(DocenteModel).filter_by(id=docente_id).first()
            if not docente:
                return False
            db.delete(docente)
            db.commit()
            return True
