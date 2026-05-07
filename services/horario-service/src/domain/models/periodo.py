from dataclasses import dataclass

@dataclass
class Periodo:
    id: int | None
    nombre: str        # "2026-1"
    tipo: str          # "SEMESTRE" o "CUATRIMESTRE"
    fecha_inicio: str
    fecha_fin: str
