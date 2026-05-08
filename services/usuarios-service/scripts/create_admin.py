#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()
# allow imports from package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.db.connection import SessionLocal
from src.infrastructure.db.models import DocenteModel
from src.infrastructure.security.hash import hash as hash_password
from sqlalchemy.exc import IntegrityError

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "adminpass")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")

def main():
    with SessionLocal() as db:
        existing = db.query(DocenteModel).filter_by(correo=ADMIN_EMAIL).first()
        if existing:
            print(f"Admin already exists: {existing.correo} (id={existing.id})")
            return

        hashed = hash_password(ADMIN_PASS)
        admin = DocenteModel(nombre=ADMIN_NAME, correo=ADMIN_EMAIL, password=hashed, rol="ADMIN", estado=True)
        db.add(admin)
        try:
            db.commit()
            db.refresh(admin)
            print(f"Admin created: id={admin.id} correo={admin.correo}")
        except IntegrityError as e:
            db.rollback()
            print("Error creating admin:", e)


if __name__ == "__main__":
    main()
