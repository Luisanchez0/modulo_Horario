from typing import Optional
from pydantic import BaseModel, field_validator


class MateriaCreateRequest(BaseModel):
    nombre: str
    codigo: str
    creditos: int
    turno: str = "AMBOS"
    descripcion: Optional[str] = None

    @field_validator("nombre", "codigo")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v

    @field_validator("creditos")
    @classmethod
    def positive_credits(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Los créditos deben ser mayores a 0")
        return v

    @field_validator("turno")
    @classmethod
    def valid_turno(cls, v: str) -> str:
        turno = str(v or "AMBOS").strip().upper()
        if turno not in {"MATUTINO", "VESPERTINO", "AMBOS"}:
            raise ValueError("El turno debe ser MATUTINO, VESPERTINO o AMBOS")
        return turno


class MateriaUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    creditos: Optional[int] = None
    turno: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator("turno")
    @classmethod
    def valid_turno(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        turno = str(v or "AMBOS").strip().upper()
        if turno not in {"MATUTINO", "VESPERTINO", "AMBOS"}:
            raise ValueError("El turno debe ser MATUTINO, VESPERTINO o AMBOS")
        return turno


class MateriaResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    creditos: int
    turno: str = "AMBOS"
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}
