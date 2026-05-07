# Ejemplos de Uso - horario-service

Este documento muestra un flujo completo para probar la generacion de horarios en el sistema.

## Requisitos previos

Debes tener levantados estos microservicios:

- `usuarios-service` en `http://localhost:8001`
- `materias-service` en `http://localhost:8002`
- `aulas-service` en `http://localhost:8003`
- `horario-service` en `http://localhost:8004`

## Logica general del flujo

`horario-service` no crea docentes, materias ni aulas por si solo.

Primero debes registrar:

1. docentes en `usuarios-service`
2. materias en `materias-service`
3. aulas en `aulas-service`
4. un periodo en `horario-service`
5. disponibilidades de docentes en `horario-service`

Despues ya puedes:

- crear horarios manualmente
- generar horarios automaticamente

## 1. Crear docentes

### Docente 1

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Juan Perez",
    "correo":"juan@unach.edu",
    "password":"123456",
    "role":"DOCENTE"
  }'
```

### Docente 2

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Maria Lopez",
    "correo":"maria@unach.edu",
    "password":"123456",
    "role":"DOCENTE"
  }'
```

## 2. Crear materias

### Materia 1

```bash
curl -X POST http://localhost:8002/api/v1/materias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Base de Datos",
    "codigo":"BD101",
    "creditos":4,
    "descripcion":"Modelo relacional y SQL"
  }'
```

### Materia 2

```bash
curl -X POST http://localhost:8002/api/v1/materias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Programacion Web",
    "codigo":"PW201",
    "creditos":4,
    "descripcion":"Frontend y backend"
  }'
```

### Materia 3

```bash
curl -X POST http://localhost:8002/api/v1/materias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Inteligencia Artificial",
    "codigo":"IA301",
    "creditos":5,
    "descripcion":"Busqueda, heuristicas y modelos"
  }'
```

## 3. Crear aulas

### Aula 1

```bash
curl -X POST http://localhost:8003/aulas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Aula A1",
    "capacidad":35
  }'
```

### Aula 2

```bash
curl -X POST http://localhost:8003/aulas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Laboratorio B2",
    "capacidad":25
  }'
```

## 4. Crear periodo

El periodo es el contenedor donde se guardan los horarios.

```bash
curl -X POST http://localhost:8004/periodos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"2026-1",
    "tipo":"SEMESTRE",
    "fecha_inicio":"2026-04-01",
    "fecha_fin":"2026-08-15"
  }'
```

## 5. Crear disponibilidades

Las disponibilidades indican en que horario puede impartir clase cada docente.

### Disponibilidad docente 1 - lunes

```bash
curl -X POST http://localhost:8004/disponibilidades \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":1,
    "dia":"LUNES",
    "hora_inicio":"08:00",
    "hora_fin":"12:00"
  }'
```

### Disponibilidad docente 1 - martes

```bash
curl -X POST http://localhost:8004/disponibilidades \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":1,
    "dia":"MARTES",
    "hora_inicio":"08:00",
    "hora_fin":"12:00"
  }'
```

### Disponibilidad docente 2 - lunes

```bash
curl -X POST http://localhost:8004/disponibilidades \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":2,
    "dia":"LUNES",
    "hora_inicio":"10:00",
    "hora_fin":"14:00"
  }'
```

### Disponibilidad docente 2 - miercoles

```bash
curl -X POST http://localhost:8004/disponibilidades \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":2,
    "dia":"MIERCOLES",
    "hora_inicio":"08:00",
    "hora_fin":"12:00"
  }'
```

### Consultar disponibilidades de un docente

```bash
curl http://localhost:8004/disponibilidades/docente/1
```

## 6. Crear un horario manual

Esto sirve para probar validaciones directas antes de usar el generador.

```bash
curl -X POST http://localhost:8004/horarios \
  -H "Content-Type: application/json" \
  -d '{
    "docente_id":1,
    "materia_id":1,
    "aula_id":1,
    "periodo_id":1,
    "dia":"LUNES",
    "hora_inicio":"08:00",
    "hora_fin":"10:00"
  }'
```

Este endpoint valida:

- que exista el docente
- que exista la materia
- que exista el aula
- que exista el periodo
- que el docente no tenga conflicto
- que el aula no este ocupada

## 7. Generar horarios automaticamente

### Ejemplo simple

Este ejemplo intenta generar horarios usando:

- periodo `1`
- bloques de `120` minutos
- jornada de `08:00` a `12:00`
- dias `LUNES` y `MARTES`
- docentes `1` y `2`
- materias `1`, `2`, `3`
- aulas `1` y `2`

```bash
curl -X POST http://localhost:8004/horarios/generar \
  -H "Content-Type: application/json" \
  -d '{
    "periodo_id":1,
    "duracion_minutos":120,
    "hora_inicio_jornada":"08:00",
    "hora_fin_jornada":"12:00",
    "dias":["LUNES","MARTES"],
    "docente_ids":[1,2],
    "materia_ids":[1,2,3],
    "aula_ids":[1,2]
  }'
```

### Ejemplo usando todos los catalogos disponibles

Si omites `docente_ids`, `materia_ids` y `aula_ids`, el servicio intenta cargar todos desde los otros microservicios.

```bash
curl -X POST http://localhost:8004/horarios/generar \
  -H "Content-Type: application/json" \
  -d '{
    "periodo_id":1,
    "duracion_minutos":120,
    "hora_inicio_jornada":"08:00",
    "hora_fin_jornada":"14:00",
    "dias":["LUNES","MARTES","MIERCOLES"]
  }'
```

## 8. Como funciona la logica de generacion

La logica actual de generacion en `horario-service` sigue este orden:

1. valida que exista el periodo
2. obtiene docentes, materias y aulas a usar
3. valida que esos IDs existan realmente en los otros microservicios
4. construye bloques horarios segun la jornada y la duracion
5. toma cada materia e intenta asignarla
6. revisa docente, dia, bloque y aula
7. valida que el docente este disponible
8. valida que no haya traslape de horario para docente o aula
9. guarda la primera combinacion valida que encuentre

## 9. Ejemplo de bloques horarios

Si mandas:

- `hora_inicio_jornada = 08:00`
- `hora_fin_jornada = 12:00`
- `duracion_minutos = 120`

Entonces se generan estos bloques:

- `08:00 - 10:00`
- `10:00 - 12:00`

## 10. Resultado esperado del generador

La respuesta puede verse asi:

```json
{
  "periodo_id": 1,
  "creados": [
    {
      "id": 1,
      "docente_id": 1,
      "materia_id": 1,
      "aula_id": 1,
      "periodo_id": 1,
      "dia": "LUNES",
      "hora_inicio": "08:00",
      "hora_fin": "10:00",
      "docente_nombre": "Juan Perez",
      "docente_correo": "juan@unach.edu",
      "materia_nombre": "Base de Datos",
      "materia_codigo": "BD101",
      "aula_nombre": "Aula A1",
      "aula_capacidad": 35
    }
  ],
  "materias_sin_asignar": [3],
  "mensajes": [
    "Se generaron 2 horarios para el periodo 1",
    "No se pudieron asignar 1 materias por falta de cupo o disponibilidad"
  ]
}
```

## 11. Consultar horarios generados

```bash
curl http://localhost:8004/horarios
```

## 12. Errores comunes

### `404 Not Found`

Puede pasar si:

- el periodo no existe
- el docente no existe al crear disponibilidad

### `400 Bad Request`

Puede pasar si:

- envias datos invalidos
- las dependencias externas no existen
- el rango de horas es invalido

### `409 Conflict`

Puede pasar al crear un horario manual si:

- el docente ya tiene clase en ese horario
- el aula ya esta ocupada

### `502 Bad Gateway`

Puede pasar si `horario-service` no logra consultar:

- `usuarios-service`
- `materias-service`
- `aulas-service`

## 13. Recomendacion de prueba

Para validar bien el flujo:

1. crea 2 docentes
2. crea 3 materias
3. crea 2 aulas
4. crea 1 periodo
5. registra disponibilidades
6. ejecuta `POST /horarios/generar`
7. consulta `GET /horarios`

Con eso puedes comprobar que la orquestacion entre microservicios esta funcionando correctamente.
