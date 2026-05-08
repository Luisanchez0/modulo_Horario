class CreateDocente:
    def __init__(self, repository, hash_service):
        self.repository = repository
        self.hash_service = hash_service

    def execute(self, data):
        if self.repository.find_by_email(data["correo"]):
            raise ValueError("El correo ya está registrado")

        data["password"] = self.hash_service(data["password"])
        role = data.get("role", "DOCENTE").upper()
        data["rol"] = "ADMIN" if role == "ADMIN" else "DOCENTE"
        data["estado"] = True
        data.pop("role", None)
        return self.repository.save(data)