class Aula:
    def __init__(self, id: int, nombre: str, capacidad: int):
        self.id = id
        self.nombre = nombre
        self.capacidad = capacidad

    def __repr__(self):
        return f'Aula(id={self.id}, nombre=\'{self.nombre}\', capacidad={self.capacidad})'
