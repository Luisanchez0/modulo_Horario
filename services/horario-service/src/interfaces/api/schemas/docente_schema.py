from pydantic import BaseModel, ConfigDict


class DocenteCreate(BaseModel):
    id: int
    nombre: str


class DocenteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
