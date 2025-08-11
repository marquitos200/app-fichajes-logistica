#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación funciona
"""

import sys
import os
from pathlib import Path

# Añadir el directorio del proyecto al path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    print("🔍 Verificando importaciones...")
    
    # Intentar importar los módulos principales
    from app.main import app
    print("✅ Aplicación FastAPI importada correctamente")
    
    from app.models import User, Company, ParteDia, ParteMensual
    print("✅ Modelos de base de datos importados correctamente")
    
    from app.auth import hash_password, verify_password
    print("✅ Módulo de autenticación importado correctamente")
    
    print("\n🎉 Todas las importaciones exitosas!")
    print("📋 La aplicación debería funcionar correctamente.")
    print("\n💡 Para ejecutar el servidor:")
    print("   python ejecutar.py")
    print("   o")
    print("   doble clic en EJECUTAR_SERVIDOR.bat")
    
except Exception as e:
    print(f"❌ Error al importar: {e}")
    print(f"📍 Tipo de error: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
