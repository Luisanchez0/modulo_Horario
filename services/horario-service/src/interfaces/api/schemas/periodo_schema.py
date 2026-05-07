from typing import Optional

from pydantic import BaseModel, ConfigDict


class PeriodoCreate(BaseModel):
    id: Optional[int] = None
    nombre: str
    tipo: str
    fecha_inicio: str
    fecha_fin: str


class PeriodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    tipo: str
    fecha_inicio: str
    fecha_fin: str
