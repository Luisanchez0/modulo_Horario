import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

from src.domain.models.horario import Horario
from src.interfaces.api.routes import horario_routes
from main import app


class FakeHorarioRepo:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.next_id = max([item.id for item in self.items], default=0) + 1

    def crear(self, horario: Horario) -> Horario:
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

    def actualizar(self, horario_id: int, horario: Horario) -> Horario:
        for index, item in enumerate(self.items):
            if item.id == horario_id:
                horario.id = horario_id
                self.items[index] = horario
                return horario
        raise ValueError(f"Horario {horario_id} no encontrado")


class FakeDisponibilidadRepo:
    def __init__(self, items=None):
        self.items = list(items or [])

    def obtener_por_docente(self, docente_id):
        return [item for item in self.items if item.docente_id == docente_id]


class FakeCatalogClient:
    def __init__(self):
        self.docente = {"id": 1, "nombre": "Docente 1", "turno": "AMBOS"}
        self.materia = {"id": 1, "nombre": "Materia 1", "turno": "AMBOS"}

    def get_current_user(self, token):
        return {"id": 1, "rol": "ADMIN"} if token else None

    def get_docente(self, docente_id: int):
        return self.docente

    def get_materia(self, materia_id: int):
        return self.materia

    def missing_docentes(self, docente_ids):
        return []

    def missing_materias(self, materia_ids):
        return []

    def missing_aulas(self, aula_ids):
        return []


@pytest.fixture()
def client():
    return TestClient(app)


def _payload(**overrides):
    base = {
        "docente_id": 1,
        "materia_id": 1,
        "aula_id": 1,
        "periodo_id": 1,
        "dia": "LUNES",
        "hora_inicio": "10:00",
        "hora_fin": "11:00",
    }
    base.update(overrides)
    return base


def test_crear_horario_rechaza_fuera_disponibilidad(monkeypatch, client):
    fake_repo = FakeHorarioRepo()
    fake_dispo_repo = FakeDisponibilidadRepo([
        type("Disp", (), {"docente_id": 1, "dia": "LUNES", "hora_inicio": "08:00", "hora_fin": "09:00"})()
    ])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: fake_dispo_repo)
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.post(
        "/horarios",
        json=_payload(),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "disponible" in response.json()["detail"].lower()


def test_actualizar_horario_rechaza_fuera_disponibilidad(monkeypatch, client):
    existente = Horario(
        id=10,
        docente_id=1,
        materia_id=1,
        aula_id=1,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="08:00",
        hora_fin="09:00",
    )
    fake_repo = FakeHorarioRepo([existente])
    fake_dispo_repo = FakeDisponibilidadRepo([
        type("Disp", (), {"docente_id": 1, "dia": "LUNES", "hora_inicio": "08:00", "hora_fin": "09:00"})()
    ])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: fake_dispo_repo)
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.put(
        "/horarios/10",
        json=_payload(),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "disponible" in response.json()["detail"].lower()


def test_crear_horario_rechaza_conflicto_docente(monkeypatch, client):
    existente = Horario(
        id=1,
        docente_id=1,
        materia_id=2,
        aula_id=2,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="10:00",
        hora_fin="11:00",
    )
    fake_repo = FakeHorarioRepo([existente])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: FakeDisponibilidadRepo())
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.post(
        "/horarios",
        json=_payload(hora_inicio="10:30", hora_fin="11:30"),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "docente" in response.json()["detail"].lower()


def test_crear_horario_rechaza_conflicto_aula(monkeypatch, client):
    existente = Horario(
        id=1,
        docente_id=2,
        materia_id=2,
        aula_id=1,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="10:00",
        hora_fin="11:00",
    )
    fake_repo = FakeHorarioRepo([existente])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: FakeDisponibilidadRepo())
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.post(
        "/horarios",
        json=_payload(hora_inicio="10:15", hora_fin="10:45"),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "aula" in response.json()["detail"].lower()


def test_actualizar_horario_rechaza_conflicto_docente(monkeypatch, client):
    existente = Horario(
        id=10,
        docente_id=1,
        materia_id=1,
        aula_id=1,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="08:00",
        hora_fin="09:00",
    )
    conflicto = Horario(
        id=11,
        docente_id=1,
        materia_id=2,
        aula_id=2,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="10:00",
        hora_fin="11:00",
    )
    fake_repo = FakeHorarioRepo([existente, conflicto])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: FakeDisponibilidadRepo())
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.put(
        "/horarios/10",
        json=_payload(hora_inicio="10:30", hora_fin="11:30"),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "docente" in response.json()["detail"].lower()


def test_actualizar_horario_rechaza_conflicto_aula(monkeypatch, client):
    existente = Horario(
        id=10,
        docente_id=1,
        materia_id=1,
        aula_id=1,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="08:00",
        hora_fin="09:00",
    )
    conflicto = Horario(
        id=11,
        docente_id=2,
        materia_id=2,
        aula_id=1,
        periodo_id=1,
        dia="LUNES",
        hora_inicio="10:00",
        hora_fin="11:00",
    )
    fake_repo = FakeHorarioRepo([existente, conflicto])

    monkeypatch.setattr(horario_routes, "_repo", lambda: fake_repo)
    monkeypatch.setattr(horario_routes, "_catalog_client", lambda: FakeCatalogClient())
    monkeypatch.setattr(horario_routes, "DisponibilidadRepositoryImpl", lambda: FakeDisponibilidadRepo())
    monkeypatch.setattr(horario_routes, "_ensure_period_exists", lambda periodo_id: None)

    response = client.put(
        "/horarios/10",
        json=_payload(hora_inicio="10:15", hora_fin="10:45"),
        headers={"Authorization": "Bearer test"},
    )

    assert response.status_code == 409
    assert "aula" in response.json()["detail"].lower()
