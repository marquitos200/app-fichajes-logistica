#!/usr/bin/env python3
"""
Script para actualizar la base de datos con la nueva tabla ParteMensual
"""
from app.models import *
from sqlmodel import SQLModel, create_engine

DB_URL = "sqlite:///app_nueva.db"
engine = create_engine(DB_URL, echo=True)

def main():
    print("🔄 Actualizando base de datos...")
    
    # Crear todas las tablas (incluida la nueva ParteMensual)
    SQLModel.metadata.create_all(engine)
    
    print("✅ Base de datos actualizada correctamente")
    print("📋 Nuevas tablas creadas:")
    print("  - ParteMensual (nueva)")

if __name__ == "__main__":
    main()
