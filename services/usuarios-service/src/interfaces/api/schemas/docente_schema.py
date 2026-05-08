from pydantic import BaseModel, ConfigDict


class DocenteCreate(BaseModel):
    matricula: str | None = None
    nombre: str
    correo: str
    password: str
    role: str = "DOCENTE"
    turno: str = "AMBOS"


class DocenteLogin(BaseModel):
    correo: str
    password: str


class DocenteUpdate(BaseModel):
    matricula: str | None = None
    nombre: str | None = None
    correo: str | None = None
    password: str | None = None
    role: str | None = None
    turno: str | None = None
    estado: bool | None = None


class DocenteResponse(BaseModel):
    id: int
    matricula: str | None = None
    nombre: str
    correo: str
    rol: str
    turno: str
    estado: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    token: str
