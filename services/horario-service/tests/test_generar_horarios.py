import sys
import unittest
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

from src.application.use_cases.disponibilidad.crear_disponibilidad import CrearDisponibilidad
from src.application.use_cases.horario.generar_horarios import GenerarHorarios
from src.domain.models.disponibilidad import Disponibilidad


class FakeHorarioRepository:
    def __init__(self):
        self.items = []
        self.next_id = 1

    def crear(self, horario):
        horario.id = self.next_id
        self.next_id += 1
        self.items.append(horario)
        return horario

    def listar(self):
        return list(self.items)

    def obtener_por_docente_y_periodo(self, docente_id, periodo_id):
        return [
            item
            for item in self.items
            if item.docente_id == docente_id and item.periodo_id == periodo_id
        ]

    def obtener_por_aula_y_periodo(self, aula_id, periodo_id):
        return [
            item
            for item in self.items
            if item.aula_id == aula_id and item.periodo_id == periodo_id
        ]


class FakeDisponibilidadRepository:
    def __init__(self, items=None):
        self.items = items or []

    def crear(self, disponibilidad):
        self.items.append(disponibilidad)
        return disponibilidad

    def obtener_por_docente(self, docente_id):
        return [item for item in self.items if item.docente_id == docente_id]


class FakePeriodoRepository:
    def obtener_por_id(self, periodo_id):
        if periodo_id != 1:
            raise ValueError(f"Periodo {periodo_id} no encontrado")
        return object()


class FakeCatalogClient:
    def __init__(self, docentes=None, materias=None):
        self._docentes = docentes or [
            {"id": 1, "nombre": "Docente 1", "turno": "AMBOS"},
        ]
        self._materias = materias or [
            {"id": 1, "nombre": "Materia 1", "turno": "AMBOS"},
        ]

    def list_docentes(self):
        return self._docentes

    def list_materias(self):
        return self._materias


class GenerarHorariosTest(unittest.TestCase):
    def test_genera_horario_con_dia_y_horas_normalizadas(self):
        horario_repo = FakeHorarioRepository()
        disponibilidad_repo = FakeDisponibilidadRepository([
            Disponibilidad(id=1, docente_id=1, dia="LUNES", hora_inicio="08:00", hora_fin="12:00")
        ])
        use_case = GenerarHorarios(
            horario_repo,
            disponibilidad_repo,
            FakePeriodoRepository(),
            FakeCatalogClient(),
        )

        creados, sin_asignar, mensajes = use_case.ejecutar(
            periodo_id=1,
            duracion_minutos=60,
            hora_inicio_jornada="8:00",
            hora_fin_jornada="10:00",
            dias=["lunes"],
            docente_ids=[1],
            materia_ids=[1],
            aula_ids=[1],
        )

        self.assertEqual(len(creados), 1)
        self.assertEqual(sin_asignar, [])
        self.assertEqual(creados[0].dia, "LUNES")
        self.assertEqual(creados[0].hora_inicio, "08:00")
        self.assertIn("Se generaron 1 horarios", mensajes[0])

    def test_usa_jornada_por_defecto_cuando_no_hay_disponibilidad(self):
        use_case = GenerarHorarios(
            FakeHorarioRepository(),
            FakeDisponibilidadRepository(),
            FakePeriodoRepository(),
            FakeCatalogClient(),
        )

        creados, sin_asignar, mensajes = use_case.ejecutar(
            periodo_id=1,
            duracion_minutos=60,
            hora_inicio_jornada="08:00",
            hora_fin_jornada="10:00",
            dias=["LUNES"],
            docente_ids=[1],
            materia_ids=[1],
            aula_ids=[1],
        )

        self.assertEqual(len(creados), 1)
        self.assertEqual(sin_asignar, [])
        self.assertTrue(any("Se generaron 1 horarios" in mensaje for mensaje in mensajes))

    def test_respeta_turno_matutino_del_docente(self):
        use_case = GenerarHorarios(
            FakeHorarioRepository(),
            FakeDisponibilidadRepository(),
            FakePeriodoRepository(),
            FakeCatalogClient(docentes=[{"id": 1, "nombre": "Docente 1", "turno": "MATUTINO"}]),
        )

        creados, sin_asignar, mensajes = use_case.ejecutar(
            periodo_id=1,
            duracion_minutos=60,
            hora_inicio_jornada="15:00",
            hora_fin_jornada="18:00",
            dias=["LUNES"],
            docente_ids=[1],
            materia_ids=[1],
            aula_ids=[1],
        )

        self.assertEqual(creados, [])
        self.assertEqual(sin_asignar, [1])
        self.assertTrue(any("No se pudieron asignar" in mensaje for mensaje in mensajes))

    def test_respeta_turno_matutino_de_materia(self):
        use_case = GenerarHorarios(
            FakeHorarioRepository(),
            FakeDisponibilidadRepository(),
            FakePeriodoRepository(),
            FakeCatalogClient(materias=[{"id": 1, "nombre": "Materia 1", "turno": "MATUTINO"}]),
        )

        creados, sin_asignar, mensajes = use_case.ejecutar(
            periodo_id=1,
            duracion_minutos=60,
            hora_inicio_jornada="15:00",
            hora_fin_jornada="18:00",
            dias=["LUNES"],
            docente_ids=[1],
            materia_ids=[1],
            aula_ids=[1],
        )

        self.assertEqual(creados, [])
        self.assertEqual(sin_asignar, [1])
        self.assertTrue(any("No se pudieron asignar" in mensaje for mensaje in mensajes))


class CrearDisponibilidadTest(unittest.TestCase):
    def test_rechaza_disponibilidad_traslapada(self):
        repo = FakeDisponibilidadRepository([
            Disponibilidad(id=1, docente_id=1, dia="LUNES", hora_inicio="08:00", hora_fin="10:00")
        ])
        use_case = CrearDisponibilidad(repo)

        with self.assertRaises(RuntimeError):
            use_case.ejecutar(None, 1, "lunes", "09:00", "11:00")

    def test_rechaza_hora_invalida(self):
        use_case = CrearDisponibilidad(FakeDisponibilidadRepository())

        with self.assertRaises(ValueError):
            use_case.ejecutar(None, 1, "LUNES", "11:00", "10:00")


if __name__ == "__main__":
    unittest.main()
