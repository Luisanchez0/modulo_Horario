from datetime import datetime
from typing import List

from src.domain.models.horario import Horario
from src.domain.models.disponibilidad import Disponibilidad


DIAS_VALIDOS = {"LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"}
TURNOS_VALIDOS = {"MATUTINO", "VESPERTINO", "AMBOS"}


class HorarioDomainService:
    @staticmethod
    def normalizar_dia(dia: str) -> str:
        dia_normalizado = dia.strip().upper()
        if dia_normalizado not in DIAS_VALIDOS:
            raise ValueError(f"Día inválido: {dia}")
        return dia_normalizado

    @staticmethod
    def normalizar_hora(hora: str) -> str:
        try:
            return datetime.strptime(hora.strip(), "%H:%M").strftime("%H:%M")
        except ValueError as exc:
            raise ValueError(f"Hora inválida: {hora}. Use formato HH:MM") from exc

    # 🔥 Validar traslape de horas
    @staticmethod
    def hay_conflicto(h1_inicio: str, h1_fin: str, h2_inicio: str, h2_fin: str) -> bool:
        return h1_inicio < h2_fin and h1_fin > h2_inicio

    # 🔥 Validar rango válido
    @staticmethod
    def validar_rango_horas(hora_inicio: str, hora_fin: str):
        hora_inicio = HorarioDomainService.normalizar_hora(hora_inicio)
        hora_fin = HorarioDomainService.normalizar_hora(hora_fin)
        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser menor a la hora de fin")

    @staticmethod
    def normalizar_turno(turno: str | None) -> str:
        turno_normalizado = str(turno or "AMBOS").strip().upper()
        if turno_normalizado not in TURNOS_VALIDOS:
            raise ValueError("Turno inválido. Use MATUTINO, VESPERTINO o AMBOS")
        return turno_normalizado

    @staticmethod
    def validar_horario_en_turno(hora_inicio: str, hora_fin: str, turno: str | None, nombre_recurso: str = "recurso"):
        turno = HorarioDomainService.normalizar_turno(turno)
        hora_inicio = HorarioDomainService.normalizar_hora(hora_inicio)
        hora_fin = HorarioDomainService.normalizar_hora(hora_fin)

        if turno == "AMBOS":
            rangos = (("07:00", "14:00"), ("15:00", "22:00"))
            if any(hora_inicio >= inicio and hora_fin <= fin for inicio, fin in rangos):
                return
            raise RuntimeError(f"El horario debe estar dentro de 07:00-14:00 o 15:00-22:00 para {nombre_recurso}")

        inicio_turno, fin_turno = ("07:00", "14:00") if turno == "MATUTINO" else ("15:00", "22:00")
        if hora_inicio < inicio_turno or hora_fin > fin_turno:
            raise RuntimeError(f"{nombre_recurso} es de turno {turno} y solo puede trabajar de {inicio_turno} a {fin_turno}")

    # 🔥 Validar conflicto de docente
    @staticmethod
    def validar_conflicto_docente(
        nuevo: Horario,
        existentes: List[Horario]
    ):
        for h in existentes:
            if h.dia == nuevo.dia and HorarioDomainService.hay_conflicto(
                nuevo.hora_inicio, nuevo.hora_fin,
                h.hora_inicio, h.hora_fin
            ):
                raise RuntimeError("Conflicto: el docente ya tiene clase en ese horario")

    # 🔥 Validar conflicto de aula
    @staticmethod
    def validar_conflicto_aula(
        nuevo: Horario,
        existentes: List[Horario]
    ):
        for h in existentes:
            if h.dia == nuevo.dia and HorarioDomainService.hay_conflicto(
                nuevo.hora_inicio, nuevo.hora_fin,
                h.hora_inicio, h.hora_fin
            ):
                raise RuntimeError("Conflicto: el aula ya está ocupada")

    # 🔥 Validar disponibilidad docente
    @staticmethod
    def validar_disponibilidad(
        nuevo: Horario,
        disponibilidades: List[Disponibilidad]
    ):
        for d in disponibilidades:
            if d.dia == nuevo.dia:
                if (nuevo.hora_inicio >= d.hora_inicio and
                        nuevo.hora_fin <= d.hora_fin):
                    return

        raise RuntimeError("El docente no está disponible en ese horario")
