class LoginDocente:
    def __init__(self, repository, verify_service, jwt_service):
        self.repository = repository
        self.verify_service = verify_service
        self.jwt_service = jwt_service

    def execute(self, correo, password):
        if hasattr(self.repository, "obtener_por_correo"):
            docente = self.repository.obtener_por_correo(correo)
        else:
            docente = self.repository.find_by_email(correo)

        if not docente:
            raise ValueError("Usuario no encontrado")

        password_hash = None
        for attr in ("password", "contrasena_hash", "contrase\u00f1a_hash"):
            candidate = getattr(docente, attr, None)
            if isinstance(candidate, (str, bytes)) and candidate:
                password_hash = candidate
                break
        if not password_hash or not self.verify_service(password, password_hash):
            raise ValueError("Credenciales incorrectas")

        # Normalizar rol antes de incluir en JWT
        rol = docente.rol or "DOCENTE"
        return self.jwt_service({"id": docente.id, "rol": rol})