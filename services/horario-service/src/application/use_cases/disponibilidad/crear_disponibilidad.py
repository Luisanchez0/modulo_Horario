from src.domain.models.disponibilidad import Disponibilidad
from src.domain.repositories.disponibilidad_repository import DisponibilidadRepository
from src.domain.services.validaciones import HorarioDomainService


class CrearDisponibilidad:

    def __init__(self, repo: DisponibilidadRepository):
        self.repo = repo

    def ejecutar(self, id: int | None, docente_id: int, dia: str, hora_inicio: str, hora_fin: str):
        dia = HorarioDomainService.normalizar_dia(dia)
        hora_inicio = HorarioDomainService.normalizar_hora(hora_inicio)
        hora_fin = HorarioDomainService.normalizar_hora(hora_fin)
        HorarioDomainService.validar_rango_horas(hora_inicio, hora_fin)

        for existente in self.repo.obtener_por_docente(docente_id):
            if existente.dia == dia and HorarioDomainService.hay_conflicto(
                hora_inicio,
                hora_fin,
                existente.hora_inicio,
                existente.hora_fin,
            ):
                raise RuntimeError("La disponibilidad se traslapa con otra del docente")

        disponibilidad = Disponibilidad(
            id=id,
            docente_id=docente_id,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        return self.repo.crear(disponibilidad)
