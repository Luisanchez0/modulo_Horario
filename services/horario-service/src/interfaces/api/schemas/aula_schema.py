from pydantic import BaseModel, ConfigDict


class AulaCreate(BaseModel):
    id: int
    nombre: str
    capacidad: int


class AulaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad: int
