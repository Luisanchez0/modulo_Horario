class LoginDocente:
    def __init__(self, repository, verify_service, jwt_service):
        self.repository = repository
        self.verify_service = verify_service
        self.jwt_service = jwt_service

    def execute(self, correo, password):
        docente = self.repository.find_by_email(correo)

        if not docente:
            raise ValueError("Usuario no encontrado")

        if not self.verify_service(password, docente.password):
            raise ValueError("Credenciales incorrectas")

        # Normalizar rol antes de incluir en JWT
        rol = docente.rol or "DOCENTE"
        return self.jwt_service({"id": docente.id, "rol": rol})