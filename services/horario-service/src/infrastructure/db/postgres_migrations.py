from sqlalchemy import text
from sqlalchemy.engine import Engine


def drop_horarios_catalog_foreign_keys(engine: Engine) -> None:
    # Keep PostgreSQL as the database, but remove local catalog FK constraints
    # so horarios-service can persist remote IDs directly.
    # Applies to horarios and disponibilidades tables.
    if not str(engine.url).startswith("postgresql"):
        return

    query = text(
        """
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
        JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = ANY(con.conkey)
        WHERE con.contype = 'f'
          AND nsp.nspname = current_schema()
          AND rel.relname = 'horarios'
          AND att.attname IN ('docente_id', 'materia_id', 'aula_id')
        """
    )

    with engine.begin() as connection:
        names = [row[0] for row in connection.execute(query).all()]
        for name in names:
            connection.execute(text(f'ALTER TABLE horarios DROP CONSTRAINT IF EXISTS "{name}"'))

        disponibilidad_query = text(
            """
            SELECT con.conname
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
            JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = ANY(con.conkey)
            WHERE con.contype = 'f'
              AND nsp.nspname = current_schema()
              AND rel.relname = 'disponibilidades'
              AND att.attname = 'docente_id'
            """
        )

        disponibilidad_names = [row[0] for row in connection.execute(disponibilidad_query).all()]
        for name in disponibilidad_names:
            connection.execute(text(f'ALTER TABLE disponibilidades DROP CONSTRAINT IF EXISTS "{name}"'))
