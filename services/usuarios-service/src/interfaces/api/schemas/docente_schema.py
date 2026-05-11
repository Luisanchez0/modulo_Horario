from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


def _validar_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres")
    if not any(char.isalpha() for char in value):
        raise ValueError("La contrasena debe incluir al menos una letra")
    if not any(char.isdigit() for char in value):
        raise ValueError("La contrasena debe incluir un numero")
    return value


class DocenteCreate(BaseModel):
    matricula: str | None = None
    nombre: str
    correo: EmailStr
    password: str
    role: str = "DOCENTE"
    turno: str = "AMBOS"

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        nombre = value.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacio")
        return nombre

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        return _validar_password(value)


class DocenteLogin(BaseModel):
    correo: EmailStr
    password: str


class DocenteUpdate(BaseModel):
    matricula: str | None = None
    nombre: str | None = None
    correo: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    turno: str | None = None
    estado: bool | None = None


class ActivationRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        return _validar_password(value)


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
