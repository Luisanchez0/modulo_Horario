from dataclasses import dataclass

@dataclass
class Horario:
    id: int | None
    docente_id: int
    materia_id: int
    aula_id: int
    periodo_id: int
    dia: str              # "LUNES", "MARTES", etc
    hora_inicio: str      # "08:00"
    hora_fin: str         # "10:00"
