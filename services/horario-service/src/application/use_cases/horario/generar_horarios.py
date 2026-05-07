from datetime import datetime, timedelta
from typing import Iterable

from src.domain.models.disponibilidad import Disponibilidad
from src.domain.models.aula import Aula
from src.domain.models.docente import Docente
from src.domain.models.horario import Horario
from src.domain.models.materia import Materia
from src.domain.repositories.disponibilidad_repository import DisponibilidadRepository
from src.domain.repositories.horario_repository import HorarioRepository
from src.domain.repositories.periodo_repository import PeriodoRepository
from src.domain.services.validaciones import HorarioDomainService
from src.infrastructure.clients.catalog_services_client import CatalogServicesClient, UpstreamServiceError


class GenerarHorarios:
    _turnos = (
        (7 * 60, 14 * 60),
        (15 * 60, 22 * 60),
    )

    _orden_dias = {
        "LUNES": 0,
        "MARTES": 1,
        "MIERCOLES": 2,
        "JUEVES": 3,
        "VIERNES": 4,
        "SABADO": 5,
    }

    def __init__(
        self,
        horario_repo: HorarioRepository,
        disponibilidad_repo: DisponibilidadRepository,
        periodo_repo: PeriodoRepository,
        catalog_client: CatalogServicesClient,
    ):
        self.horario_repo = horario_repo
        self.disponibilidad_repo = disponibilidad_repo
        self.periodo_repo = periodo_repo
        self.catalog_client = catalog_client

    def ejecutar(
        self,
        periodo_id: int,
        duracion_minutos: int = 60,
        hora_inicio_jornada: str = "08:00",
        hora_fin_jornada: str = "18:00",
        dias: list[str] | None = None,
        docente_ids: list[int] | None = None,
        materia_ids: list[int] | None = None,
        aula_ids: list[int] | None = None,
    ) -> tuple[list[Horario], list[int], list[str]]:
        if duracion_minutos <= 0:
            raise ValueError("La duración debe ser mayor a cero")

        self.periodo_repo.obtener_por_id(periodo_id)

        docentes = self._docentes_para_generacion(docente_ids)
        materias = self._materias_para_generacion(materia_ids)
        aulas = self._aulas_para_generacion(aula_ids)

        if not docentes:
            raise ValueError("No hay docentes disponibles para generar horarios")
        if not materias:
            raise ValueError("No hay materias disponibles para generar horarios")
        if not aulas:
            raise ValueError("No hay aulas disponibles para generar horarios")

        dias_trabajo = [
            HorarioDomainService.normalizar_dia(dia)
            for dia in (dias or ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"])
        ]
        hora_inicio_jornada = HorarioDomainService.normalizar_hora(hora_inicio_jornada)
        hora_fin_jornada = HorarioDomainService.normalizar_hora(hora_fin_jornada)
        HorarioDomainService.validar_rango_horas(hora_inicio_jornada, hora_fin_jornada)

        slots = self._construir_slots(hora_inicio_jornada, hora_fin_jornada, duracion_minutos)
        if not slots:
            raise ValueError("No se pudieron construir bloques horarios válidos")

        disponibilidades = {
            docente.id: self._disponibilidades_o_jornada_por_defecto(
                docente_id=docente.id,
                disponibilidades=self.disponibilidad_repo.obtener_por_docente(docente.id),
                dias=dias_trabajo,
                hora_inicio=hora_inicio_jornada,
                hora_fin=hora_fin_jornada,
            )
            for docente in docentes
        }
        existentes = [
            horario
            for horario in self.horario_repo.listar()
            if horario.periodo_id == periodo_id
        ]
        creados: list[Horario] = []
        materias_sin_asignar: list[int] = []
        motivos_sin_asignar: dict[int, str] = {}

        for indice, materia in enumerate(materias):
            docente_preferido = docentes[indice % len(docentes)]
            asignado = False
            orden_docentes = self._rotar(docentes, docente_preferido)
            tuvo_disponibilidad = False
            tuvo_slot_sin_conflicto = False
            mejor_candidato: tuple[int, int, int, int, int, Horario] | None = None

            for docente in orden_docentes:
                disponibilidades_docente = disponibilidades.get(docente.id, [])

                for dia in dias_trabajo:
                    for hora_inicio, hora_fin in slots:
                        if not self._docente_disponible(
                            disponibilidades_docente,
                            dia,
                            hora_inicio,
                            hora_fin,
                        ):
                            continue
                        tuvo_disponibilidad = True

                        for aula in aulas:
                            candidato = Horario(
                                id=None,
                                docente_id=docente.id,
                                materia_id=materia.id,
                                aula_id=aula.id,
                                periodo_id=periodo_id,
                                dia=dia,
                                hora_inicio=hora_inicio,
                                hora_fin=hora_fin,
                            )

                            if not self._es_turno_compatible(docente.turno, candidato.hora_inicio, candidato.hora_fin):
                                continue

                            if self._tiene_conflicto(candidato, existentes + creados):
                                continue
                            tuvo_slot_sin_conflicto = True

                            puntaje = self._puntuar_candidato(
                                candidato,
                                existentes + creados,
                                docente_preferido.id,
                                docente.turno,
                            )
                            candidato_actual = (
                                puntaje,
                                self._dia_index(candidato.dia) * -1,
                                self._hora_a_minutos(candidato.hora_inicio) * -1,
                                1 if candidato.docente_id == docente_preferido.id else 0,
                                -aula.id,
                                candidato,
                            )
                            if mejor_candidato is None or candidato_actual > mejor_candidato:
                                mejor_candidato = candidato_actual

                        if asignado:
                            break

                    if asignado:
                        break

                if asignado:
                    break

            if mejor_candidato is not None:
                _, _, _, _, _, candidato = mejor_candidato
                creado = self.horario_repo.crear(candidato)
                creados.append(creado)
                existentes.append(creado)
                asignado = True

            if not asignado:
                materias_sin_asignar.append(materia.id)
                if not tuvo_disponibilidad:
                    motivos_sin_asignar[materia.id] = "Sin disponibilidad docente en los días y bloques solicitados"
                elif not tuvo_slot_sin_conflicto:
                    motivos_sin_asignar[materia.id] = "Todos los bloques disponibles tienen conflicto de docente o aula"
                else:
                    motivos_sin_asignar[materia.id] = "No se encontró una combinación válida"

        mensajes = [
            f"Se generaron {len(creados)} horarios para el periodo {periodo_id}",
        ]
        if materias_sin_asignar:
            mensajes.append(
                f"No se pudieron asignar {len(materias_sin_asignar)} materias por falta de cupo o disponibilidad"
            )
            for materia_id in materias_sin_asignar:
                mensajes.append(f"Materia {materia_id}: {motivos_sin_asignar[materia_id]}")

        return creados, materias_sin_asignar, mensajes

    def _docentes_para_generacion(self, docente_ids: list[int] | None) -> list[Docente]:
        if docente_ids is None:
            return []

        try:
            docentes_catalogo = self.catalog_client.list_docentes()
        except UpstreamServiceError as exc:
            raise ValueError(str(exc)) from exc

        docentes_filtrados = []
        ids_permitidos = set(docente_ids)
        for docente in docentes_catalogo:
            docente_id = int(docente.get("id", 0))
            if docente_id not in ids_permitidos:
                continue
            docentes_filtrados.append(
                Docente(
                    id=docente_id,
                    nombre=docente.get("nombre", f"Docente {docente_id}"),
                    turno=self._normalizar_turno_docente(docente.get("turno")),
                )
            )

        return sorted(docentes_filtrados, key=lambda docente: docente.id) if docentes_filtrados else []

    def _materias_para_generacion(self, materia_ids: list[int] | None) -> list[Materia]:
        if materia_ids is None:
            return []
        try:
            materias_catalogo = self.catalog_client.list_materias()
        except UpstreamServiceError as exc:
            raise ValueError(str(exc)) from exc

        materias_filtradas = []
        ids_permitidos = set(materia_ids)
        for materia in materias_catalogo:
            materia_id = int(materia.get("id", 0))
            if materia_id not in ids_permitidos:
                continue
            materias_filtradas.append(
                Materia(
                    id=materia_id,
                    nombre=materia.get("nombre", f"Materia {materia_id}"),
                    turno=self._normalizar_turno(materia.get("turno")),
                )
            )

        return sorted(materias_filtradas, key=lambda materia: materia.id)

    def _aulas_para_generacion(self, aula_ids: list[int] | None) -> list[Aula]:
        if aula_ids is None:
            return []
        return [Aula(id=aula_id, nombre=f"Aula {aula_id}", capacidad=0) for aula_id in sorted(set(aula_ids))]

    @staticmethod
    def _disponibilidades_o_jornada_por_defecto(
        docente_id: int,
        disponibilidades: list[Disponibilidad],
        dias: list[str],
        hora_inicio: str,
        hora_fin: str,
    ) -> list[Disponibilidad]:
        if disponibilidades:
            return disponibilidades

        return [
            Disponibilidad(
                id=None,
                docente_id=docente_id,
                dia=dia,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
            for dia in dias
        ]

    @staticmethod
    def _normalizar_turno_docente(turno: str | None) -> str:
        return GenerarHorarios._normalizar_turno(turno)

    @staticmethod
    def _normalizar_turno(turno: str | None) -> str:
        value = str(turno or "AMBOS").strip().upper()
        if value in {"MATUTINO", "VESPERTINO", "AMBOS"}:
            return value
        return "AMBOS"

    @staticmethod
    def _filtrar(items: Iterable, ids: list[int] | None):
        if ids is None:
            return list(items)
        allowed = set(ids)
        return [item for item in items if item.id in allowed]

    @staticmethod
    def _rotar(docentes: list[Docente], docente_preferido: Docente) -> list[Docente]:
        if docente_preferido not in docentes:
            return docentes

        indice = docentes.index(docente_preferido)
        return docentes[indice:] + docentes[:indice]

    @staticmethod
    def _construir_slots(
        hora_inicio_jornada: str,
        hora_fin_jornada: str,
        duracion_minutos: int,
    ) -> list[tuple[str, str]]:
        slots: list[tuple[str, str]] = []
        inicio_jornada = GenerarHorarios._hora_a_minutos(hora_inicio_jornada)
        fin_jornada = GenerarHorarios._hora_a_minutos(hora_fin_jornada)
        delta = timedelta(minutes=duracion_minutos)

        for turno_inicio, turno_fin in GenerarHorarios._turnos:
            inicio = max(inicio_jornada, turno_inicio)
            fin = min(fin_jornada, turno_fin)
            cursor = datetime.strptime(f"{inicio // 60:02d}:{inicio % 60:02d}", "%H:%M")
            limite = datetime.strptime(f"{fin // 60:02d}:{fin % 60:02d}", "%H:%M")

            while cursor + delta <= limite:
                slot_fin = cursor + delta
                slots.append((cursor.strftime("%H:%M"), slot_fin.strftime("%H:%M")))
                cursor = slot_fin

        return slots

    @staticmethod
    def _docente_disponible(
        disponibilidades,
        dia: str,
        hora_inicio: str,
        hora_fin: str,
    ) -> bool:
        for disponibilidad in disponibilidades:
            if disponibilidad.dia == dia:
                if disponibilidad.hora_inicio <= hora_inicio and disponibilidad.hora_fin >= hora_fin:
                    return True
        return False

    @staticmethod
    def _hay_conflicto(hora_inicio_1: str, hora_fin_1: str, hora_inicio_2: str, hora_fin_2: str) -> bool:
        return hora_inicio_1 < hora_fin_2 and hora_inicio_2 < hora_fin_1

    @classmethod
    def _dia_index(cls, dia: str) -> int:
        return cls._orden_dias.get(dia, len(cls._orden_dias))

    @staticmethod
    def _hora_a_minutos(hora: str) -> int:
        horas, minutos = hora.split(":")
        return int(horas) * 60 + int(minutos)

    @classmethod
    def _puntuar_candidato(cls, candidato: Horario, existentes: list[Horario], docente_preferido_id: int, turno_docente: str = "AMBOS") -> int:
        puntaje = 0
        clases_docente = [horario for horario in existentes if horario.docente_id == candidato.docente_id]
        clases_mismo_dia = [horario for horario in clases_docente if horario.dia == candidato.dia]
        dias_con_clases = {horario.dia for horario in clases_docente}
        turno_candidato = cls._turno_de_hora(candidato.hora_inicio)

        if turno_docente in {"MATUTINO", "VESPERTINO"} and turno_candidato is not None:
            if turno_candidato != (0 if turno_docente == "MATUTINO" else 1):
                return -10_000

        if candidato.docente_id == docente_preferido_id:
            puntaje += 15

        if clases_mismo_dia:
            puntaje += 150

        if turno_candidato is not None and any(
            cls._turno_de_hora(horario.hora_inicio) == turno_candidato for horario in clases_docente
        ):
            puntaje += 120

        if cls._tiene_dia_cercano(candidato.dia, dias_con_clases):
            puntaje += 50

        candidato_inicio = cls._hora_a_minutos(candidato.hora_inicio)
        candidato_fin = cls._hora_a_minutos(candidato.hora_fin)

        for clase in clases_mismo_dia:
            inicio_clase = cls._hora_a_minutos(clase.hora_inicio)
            fin_clase = cls._hora_a_minutos(clase.hora_fin)

            if candidato_inicio == fin_clase or candidato_fin == inicio_clase:
                puntaje += 80
            else:
                distancia = min(abs(candidato_inicio - fin_clase), abs(candidato_fin - inicio_clase))
                puntaje += max(0, 40 - distancia // 8)

        if not clases_mismo_dia and clases_docente:
            puntaje += 20

        return puntaje

    @classmethod
    def _tiene_dia_cercano(cls, dia: str, dias_existentes: set[str]) -> bool:
        indice = cls._dia_index(dia)
        return any(abs(indice - cls._dia_index(dia_existente)) == 1 for dia_existente in dias_existentes)

    @staticmethod
    def _es_turno_compatible(turno_recurso: str, hora_inicio: str, hora_fin: str) -> bool:
        turno = GenerarHorarios._normalizar_turno(turno_recurso)
        if turno == "MATUTINO":
            return hora_inicio >= "07:00" and hora_fin <= "14:00"
        if turno == "VESPERTINO":
            return hora_inicio >= "15:00" and hora_fin <= "22:00"
        if turno == "AMBOS":
            return (
                ("07:00" <= hora_inicio and hora_fin <= "14:00")
                or ("15:00" <= hora_inicio and hora_fin <= "22:00")
            )
        return True

    @classmethod
    def _turno_de_hora(cls, hora: str) -> int | None:
        minutos = cls._hora_a_minutos(hora)
        for indice, (inicio, fin) in enumerate(cls._turnos):
            if inicio <= minutos < fin:
                return indice
        return None

    def _tiene_conflicto(self, candidato: Horario, existentes: list[Horario]) -> bool:
        for horario in existentes:
            if horario.dia != candidato.dia:
                continue

            if horario.docente_id == candidato.docente_id and self._hay_conflicto(
                candidato.hora_inicio,
                candidato.hora_fin,
                horario.hora_inicio,
                horario.hora_fin,
            ):
                return True

            if horario.aula_id == candidato.aula_id and self._hay_conflicto(
                candidato.hora_inicio,
                candidato.hora_fin,
                horario.hora_inicio,
                horario.hora_fin,
            ):
                return True

        return False
