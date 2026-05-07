from dataclasses import dataclass

@dataclass
class Materia:
    id: int
    nombre: str
    turno: str = "AMBOS"
