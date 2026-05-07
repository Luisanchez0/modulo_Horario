from src.domain.repositories.horario_repository import HorarioRepository


class ObtenerHorarios:

    def __init__(self, repo: HorarioRepository):
        self.repo = repo

    def ejecutar(self):
        return self.repo.listar()