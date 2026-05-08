from dataclasses import dataclass
from typing import Optional


@dataclass
class Materia:
    nombre: str
    codigo: str
    creditos: int
    turno: str = "AMBOS"
    descripcion: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la materia no puede estar vacío")
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código de la materia no puede estar vacío")
        if self.creditos <= 0:
            raise ValueError("Los créditos deben ser mayores a 0")
        self.turno = self._normalizar_turno(self.turno)

    @staticmethod
    def _normalizar_turno(value: str | None) -> str:
        turno = str(value or "AMBOS").strip().upper()
        if turno in {"MATUTINO", "VESPERTINO", "AMBOS"}:
            return turno
        raise ValueError("El turno debe ser MATUTINO, VESPERTINO o AMBOS")
