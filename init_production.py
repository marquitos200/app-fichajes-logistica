#!/usr/bin/env python3
"""
Script para inicializar la aplicación en producción
"""

import os
from sqlmodel import SQLModel
from app.models import Company, User, ParteDia, ParteMensual, Ruta
from app.auth import hash_password

# Configuración de base de datos para producción
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app_nueva.db")

# Para PostgreSQL en producción
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

from sqlmodel import create_engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def init_production():
    """Inicializar la aplicación para producción"""
    print("🚀 Inicializando aplicación para producción...")
    
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)
    print("✅ Tablas creadas")
    
    # Crear empresa de ejemplo si no existe
    from sqlmodel import Session
    with Session(engine) as db:
        # Verificar si ya existe una empresa
        from sqlmodel import select
        existing_company = db.exec(select(Company)).first()
        
        if not existing_company:
            # Crear empresa de ejemplo
            company = Company(
                name="Mi Empresa Logística",
                company_key="DEMO2025"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            
            # Crear usuario admin de ejemplo
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                company_id=company.id
            )
            db.add(admin_user)
            db.commit()
            
            print("✅ Empresa y usuario admin creados")
            print(f"🏢 Empresa: {company.name}")
            print(f"🔑 Clave: {company.company_key}")
            print(f"👤 Admin: admin / admin123")
        else:
            print("✅ Empresa ya existe, saltando creación")
    
    print("🎉 Aplicación lista para producción!")

if __name__ == "__main__":
    init_production()
