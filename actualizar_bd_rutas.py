#!/usr/bin/env python3
"""
Script para actualizar la base de datos añadiendo la tabla Ruta
"""

from sqlmodel import SQLModel, create_engine
from app.models import Company, User, ParteDia, ParteMensual, Ruta

# Crear la conexión a la base de datos
engine = create_engine("sqlite:///app_nueva.db")

def actualizar_bd():
    print("🔄 Actualizando base de datos para añadir tabla Ruta...")
    
    try:
        # Crear todas las tablas (incluyendo la nueva tabla Ruta)
        SQLModel.metadata.create_all(engine)
        print("✅ Tabla Ruta creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if actualizar_bd():
        print("🎉 Base de datos actualizada correctamente")
        print("📝 La tabla Ruta está lista para almacenar múltiples rutas por parte")
    else:
        print("💥 Error en la actualización")
