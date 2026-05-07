from dataclasses import dataclass

@dataclass
class Disponibilidad:
    id: int | None
    docente_id: int
    dia: str
    hora_inicio: str
    hora_fin: str
