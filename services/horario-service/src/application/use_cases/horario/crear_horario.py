from src.domain.models.horario import Horario
from src.domain.repositories.horario_repository import HorarioRepository
from src.domain.services.validaciones import HorarioDomainService


def hay_conflicto(hora_inicio_1, hora_fin_1, hora_inicio_2, hora_fin_2):
    return hora_inicio_1 < hora_fin_2 and hora_inicio_2 < hora_fin_1


class CrearHorario:

    def __init__(self, repo: HorarioRepository):
        self.repo = repo

    def ejecutar(self, horario: Horario):
        horario.dia = HorarioDomainService.normalizar_dia(horario.dia)
        horario.hora_inicio = HorarioDomainService.normalizar_hora(horario.hora_inicio)
        horario.hora_fin = HorarioDomainService.normalizar_hora(horario.hora_fin)
        HorarioDomainService.validar_rango_horas(horario.hora_inicio, horario.hora_fin)

        # 🔥 validar conflicto docente
        horarios_docente = self.repo.obtener_por_docente_y_periodo(
            horario.docente_id,
            horario.periodo_id
        )

        for h in horarios_docente:
            if h.dia == horario.dia and hay_conflicto(
                horario.hora_inicio, horario.hora_fin,
                h.hora_inicio, h.hora_fin
            ):
                raise RuntimeError("El docente ya tiene clase en ese horario")

        # 🔥 validar conflicto aula
        horarios_aula = self.repo.obtener_por_aula_y_periodo(
            horario.aula_id,
            horario.periodo_id
        )

        for h in horarios_aula:
            if h.dia == horario.dia and hay_conflicto(
                horario.hora_inicio, horario.hora_fin,
                h.hora_inicio, h.hora_fin
            ):
                raise RuntimeError("El aula ya está ocupada")

        return self.repo.crear(horario)
