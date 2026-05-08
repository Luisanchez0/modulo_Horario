import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing required environment variable: DATABASE_URL")

def create_database_if_not_exists(database_url: str):
    url = make_url(database_url)
    database_name = url.database

    if not database_name:
        return

    root_url = url.set(database=None)
    engine = create_engine(root_url)

    with engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        connection.commit()

    engine.dispose()


create_database_if_not_exists(DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def ensure_docentes_turno_column():
    """Ensure turno column exists in docentes table (MySQL-compatible)"""
    with engine.begin() as connection:
        # Check if column exists in MySQL
        result = connection.execute(
            text(
                """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_NAME='docentes' AND COLUMN_NAME='turno'"""
            )
        )
        if result.fetchone() is None:
            # Column doesn't exist, add it
            connection.execute(
                text(
                    "ALTER TABLE docentes ADD COLUMN turno VARCHAR(20) NOT NULL DEFAULT 'AMBOS'"
                )
            )


def ensure_docentes_matricula_column():
    """Ensure matricula column exists in docentes table (MySQL-compatible)."""
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_NAME='docentes' AND COLUMN_NAME='matricula'"""
            )
        )
        if result.fetchone() is None:
            connection.execute(
                text(
                    "ALTER TABLE docentes ADD COLUMN matricula VARCHAR(50) NULL UNIQUE"
                )
            )
