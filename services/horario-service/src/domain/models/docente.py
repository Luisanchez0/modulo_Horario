from dataclasses import dataclass


@dataclass
class Docente:
    id: int
    nombre: str
    turno: str = "AMBOS"