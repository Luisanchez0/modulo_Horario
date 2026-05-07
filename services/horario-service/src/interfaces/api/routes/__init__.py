from .aula_routes import router as aula_router
from .disponibilidad_routes import router as disponibilidad_router
from .docente_routes import router as docente_router
from .horario_routes import router as horario_router
from .materia_routes import router as materia_router
from .periodo_routes import router as periodo_router

routers = [
    aula_router,
    docente_router,
    materia_router,
    periodo_router,
    disponibilidad_router,
    horario_router,
]
