# Aulas Service

Microservicio para gestionar aulas, parte del sistema de generación de horarios.

## Arquitectura

Sigue la arquitectura hexagonal con las siguientes capas:
- **Domain**: Entidades y repositorios (core business logic)
- **Application**: Servicios de aplicación (use cases)
- **Infrastructure**: Adaptadores para DB y HTTP

## Requisitos

- Python 3.8+
- MySQL

## Instalación

1. Clona o descarga el proyecto.
2. Crea un entorno virtual: python -m venv venv
3. Activa el entorno: env\Scripts\activate (Windows)
4. Instala dependencias: pip install -r requirements.txt

## Configuración de Base de Datos

1. Instala y configura MySQL.
2. Crea una base de datos llamada ulas_db.
3. Actualiza las credenciales en src/infrastructure/http/aula_controller.py:
   `python
   database_url = 'mysql+pymysql://tu_usuario:tu_password@localhost/aulas_db'
   `

## Ejecución

Ejecuta el servicio: python src/app.py o uvicorn src.infrastructure.http.aula_controller:app --reload

El servicio estará disponible en http://localhost:8000

## Documentación de la API

FastAPI genera automáticamente documentación interactiva en http://localhost:8000/docs

## Endpoints

- GET /aulas: Obtener todas las aulas
- GET /aulas/{aula_id}: Obtener aula por ID
- POST /aulas: Crear nueva aula (JSON: {nombre, capacidad})
- PUT /aulas/{aula_id}: Actualizar aula (JSON: {nombre, capacidad})
- DELETE /aulas/{aula_id}: Eliminar aula
