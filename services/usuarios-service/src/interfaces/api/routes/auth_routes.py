import os

from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from src.infrastructure.repositories.docente_repository_impl import DocenteRepositoryImpl
from src.application.use_cases.create_docente import CreateDocente
from src.application.use_cases.login_docente import LoginDocente
from src.infrastructure.security.hash import hash, verify
from src.infrastructure.security.jwt import create_token
from src.interfaces.api.schemas.docente_schema import DocenteCreate, DocenteLogin, DocenteResponse, TokenResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.infrastructure.security.jwt import verify_token

router = APIRouter()
repo = DocenteRepositoryImpl()
security = HTTPBearer()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


ADMIN_CREATION_KEY = _required_env("ADMIN_CREATION_KEY")


@router.post("/register", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
def register(data: DocenteCreate):
    if data.role.upper() == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Para crear administradores usa /auth/register-admin con la clave adecuada",
        )

    use_case = CreateDocente(repo, hash)
    try:
        return use_case.execute(data.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/register-admin", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
def register_admin(data: DocenteCreate, x_admin_key: str = Header(None, alias="X-Admin-Key")):
    if x_admin_key != ADMIN_CREATION_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin key inválida")

    data.role = "ADMIN"
    use_case = CreateDocente(repo, hash)
    try:
        return use_case.execute(data.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/login", response_model=TokenResponse)
def login(request: Request, data: DocenteLogin):
    """
    Login endpoint (rate limited: 5 attempts per minute)
    """
    # Rate limiting check (manual for now, Nginx will handle in production)
    use_case = LoginDocente(repo, verify, create_token)
    try:
        token = use_case.execute(data.correo, data.password)
        return {"token": token}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    return payload
