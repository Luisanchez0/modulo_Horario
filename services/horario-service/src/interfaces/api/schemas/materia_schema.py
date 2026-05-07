from pydantic import BaseModel, ConfigDict


class MateriaCreate(BaseModel):
    id: int
    nombre: str


class MateriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
