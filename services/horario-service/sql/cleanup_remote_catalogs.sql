-- Cleanup for remote-catalog mode in horario-service (PostgreSQL)
-- Run this manually when you are sure horarios-service no longer relies on local catalog tables.

BEGIN;

-- Remove local catalog tables now managed by other microservices.
DROP TABLE IF EXISTS docentes CASCADE;
DROP TABLE IF EXISTS materias CASCADE;
DROP TABLE IF EXISTS aulas CASCADE;

COMMIT;
