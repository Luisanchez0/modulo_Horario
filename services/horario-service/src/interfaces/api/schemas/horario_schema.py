from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.domain.services.validaciones import HorarioDomainService


class HorarioCreate(BaseModel):
    id: Optional[int] = None
    docente_id: int
    materia_id: int
    aula_id: int
    periodo_id: int
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


class HorarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    docente_id: int
    materia_id: int
    aula_id: int
    periodo_id: int
    dia: str
    hora_inicio: str
    hora_fin: str
    docente_nombre: Optional[str] = None
    docente_correo: Optional[str] = None
    materia_nombre: Optional[str] = None
    materia_codigo: Optional[str] = None
    materia_turno: Optional[str] = None
    aula_nombre: Optional[str] = None
    aula_capacidad: Optional[int] = None


class GenerarHorariosRequest(BaseModel):
    periodo_id: int
    duracion_minutos: int = Field(default=120, gt=0)
    hora_inicio_jornada: str = "08:00"
    hora_fin_jornada: str = "18:00"
    dias: list[str] = Field(default_factory=lambda: ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"])
    docente_ids: Optional[list[int]] = None
    materia_ids: Optional[list[int]] = None
    aula_ids: Optional[list[int]] = None

    @field_validator("hora_inicio_jornada", "hora_fin_jornada")
    @classmethod
    def validar_hora(cls, value: str) -> str:
        return HorarioDomainService.normalizar_hora(value)

    @field_validator("dias")
    @classmethod
    def validar_dias(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("Debe indicar al menos un día")
        return [HorarioDomainService.normalizar_dia(dia) for dia in value]

    @model_validator(mode="after")
    def validar_rango_jornada(self):
        HorarioDomainService.validar_rango_horas(self.hora_inicio_jornada, self.hora_fin_jornada)
        return self


class GenerarHorariosResponse(BaseModel):
    periodo_id: int
    creados: list[HorarioRead]
    materias_sin_asignar: list[int]
    mensajes: list[str]
