class Docente:
    def __init__(self, id, nombre, correo, password, rol="DOCENTE", estado=True):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password = password
        self.rol = rol
        self.estado = estado