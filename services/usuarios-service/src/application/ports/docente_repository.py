from abc import ABC, abstractmethod

class DocenteRepository(ABC):

    @abstractmethod
    def save(self, docente):
        pass

    @abstractmethod
    def find_by_email(self, correo):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, docente_id, data):
        pass

    @abstractmethod
    def delete(self, docente_id):
        pass