from typing import Iterable

import requests

from src.core.config import settings


class UpstreamServiceError(Exception):
    pass


class CatalogServicesClient:
    def __init__(self) -> None:
        self._timeout = settings.upstream_timeout_seconds

    def docente_exists(self, docente_id: int) -> bool:
        url = f"{settings.usuarios_service_url}/internal/docentes/{docente_id}"
        return self._exists(url, headers={"X-Internal-Key": settings.internal_api_key})

    def materia_exists(self, materia_id: int) -> bool:
        url = f"{settings.materias_service_url}/api/v1/materias/{materia_id}"
        return self._exists(url)

    def aula_exists(self, aula_id: int) -> bool:
        url = f"{settings.aulas_service_url}/aulas/{aula_id}"
        return self._exists(url)

    def get_docente(self, docente_id: int) -> dict | None:
        url = f"{settings.usuarios_service_url}/internal/docentes/{docente_id}"
        return self._get_json(url, headers={"X-Internal-Key": settings.internal_api_key})

    def get_materia(self, materia_id: int) -> dict | None:
        url = f"{settings.materias_service_url}/api/v1/materias/{materia_id}"
        return self._get_json(url)

    def get_aula(self, aula_id: int) -> dict | None:
        url = f"{settings.aulas_service_url}/aulas/{aula_id}"
        return self._get_json(url)

    def list_materias(self) -> list[dict]:
        url = f"{settings.materias_service_url}/api/v1/materias/"
        return self._get_json_list(url)

    def list_aulas(self) -> list[dict]:
        url = f"{settings.aulas_service_url}/aulas"
        return self._get_json_list(url)

    def list_docentes(self) -> list[dict]:
        url = f"{settings.usuarios_service_url}/internal/docentes"
        return self._get_json_list(url, headers={"X-Internal-Key": settings.internal_api_key})

    def get_current_user(self, token: str | None) -> dict | None:
        if not token:
            return None
        headers = {"Authorization": token}
        url = f"{settings.usuarios_service_url}/auth/me"
        return self._get_json(url, headers=headers)

    def get_horario_labels(self, docente_id: int, materia_id: int, aula_id: int) -> dict[str, str | None]:
        docente = self.get_docente(docente_id)
        materia = self.get_materia(materia_id)
        aula = self.get_aula(aula_id)
        return {
            "docente_nombre": (docente or {}).get("nombre"),
            "docente_correo": (docente or {}).get("correo"),
            "materia_nombre": (materia or {}).get("nombre"),
            "materia_codigo": (materia or {}).get("codigo"),
            "materia_turno": (materia or {}).get("turno"),
            "aula_nombre": (aula or {}).get("nombre"),
            "aula_capacidad": (aula or {}).get("capacidad"),
        }

    def missing_docentes(self, docente_ids: Iterable[int]) -> list[int]:
        return [docente_id for docente_id in self._normalized_ids(docente_ids) if not self.docente_exists(docente_id)]

    def missing_materias(self, materia_ids: Iterable[int]) -> list[int]:
        return [materia_id for materia_id in self._normalized_ids(materia_ids) if not self.materia_exists(materia_id)]

    def missing_aulas(self, aula_ids: Iterable[int]) -> list[int]:
        return [aula_id for aula_id in self._normalized_ids(aula_ids) if not self.aula_exists(aula_id)]

    def _exists(self, url: str, headers: dict[str, str] | None = None) -> bool:
        try:
            response = requests.get(url, headers=headers or {}, timeout=self._timeout)
        except requests.RequestException as exc:
            raise UpstreamServiceError(f"No se pudo consultar servicio externo: {url}") from exc

        if response.status_code == 404:
            return False
        if response.status_code >= 400:
            raise UpstreamServiceError(
                f"Error consultando servicio externo ({response.status_code}) en {url}"
            )

        return True

    def _get_json(self, url: str, headers: dict[str, str] | None = None) -> dict | None:
        try:
            response = requests.get(url, headers=headers or {}, timeout=self._timeout)
        except requests.RequestException as exc:
            raise UpstreamServiceError(f"No se pudo consultar servicio externo: {url}") from exc

        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise UpstreamServiceError(
                f"Error consultando servicio externo ({response.status_code}) en {url}"
            )

        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return None

    def _get_json_list(self, url: str, headers: dict[str, str] | None = None) -> list[dict]:
        try:
            response = requests.get(url, headers=headers or {}, timeout=self._timeout)
        except requests.RequestException as exc:
            raise UpstreamServiceError(f"No se pudo consultar servicio externo: {url}") from exc

        if response.status_code >= 400:
            raise UpstreamServiceError(
                f"Error consultando servicio externo ({response.status_code}) en {url}"
            )

        payload = response.json()
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    @staticmethod
    def _normalized_ids(ids: Iterable[int]) -> list[int]:
        return sorted(set(ids))
