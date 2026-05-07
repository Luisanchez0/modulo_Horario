from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from src.domain.services.validaciones import HorarioDomainService


class DisponibilidadCreate(BaseModel):
    id: Optional[int] = None
    docente_id: int
    dia: str
    hora_inicio: str
    hora_fin: str

    @field_validator("dia")
    @classmethod
    def validar_dia(cls, value: str) -> str:
        return HorarioDomainService.normalizar_dia(value)

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def validar_hora(cls, value: str) -> str:
        return HorarioDomainService.normalizar_hora(value)

    @model_validator(mode="after")
    def validar_rango(self):
        HorarioDomainService.validar_rango_horas(self.hora_inicio, self.hora_fin)
        return self


class DisponibilidadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    docente_id: int
    dia: str
    hora_inicio: str
    hora_fin: str
