#!/usr/bin/env python3
"""
Script para ejecutar el servidor FastAPI
Sistema de Fichajes Logística
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuración
PROJECT_DIR = Path(__file__).parent
VENV_PATH = PROJECT_DIR.parent / '.venv'
PYTHON_EXE = VENV_PATH / 'Scripts' / 'python.exe'
UVICORN_EXE = VENV_PATH / 'Scripts' / 'uvicorn.exe'

def main():
    print("=" * 60)
    print("    🚀 SISTEMA DE FICHAJES LOGÍSTICA")
    print("=" * 60)
    print()
    
    # Verificar que el entorno virtual existe
    if not PYTHON_EXE.exists():
        print(f"❌ Error: No se encuentra el entorno virtual en {VENV_PATH}")
        print("   Ejecuta: python -m venv .venv")
        return 1
    
    # Verificar que uvicorn está instalado
    if not UVICORN_EXE.exists():
        print("❌ Error: uvicorn no está instalado")
        print("   Ejecuta: pip install uvicorn[standard]")
        return 1
    
    # Cambiar al directorio del proyecto
    os.chdir(PROJECT_DIR)
    print(f"📁 Directorio de trabajo: {PROJECT_DIR}")
    print()
    
    # Información del servidor
    print("🌐 El servidor estará disponible en:")
    print("   http://127.0.0.1:8000")
    print()
    print("📋 Páginas principales:")
    print("   • Registro:    http://127.0.0.1:8000/register")
    print("   • Login:       http://127.0.0.1:8000/login")
    print("   • Repartidor:  http://127.0.0.1:8000/repartidor")
    print("   • Admin:       http://127.0.0.1:8000/admin")
    print()
    print("=" * 60)
    print("🔥 Iniciando servidor... (Ctrl+C para detener)")
    print("=" * 60)
    print()
    
    # Ejecutar uvicorn
    try:
        cmd = [
            str(UVICORN_EXE),
            "app.main:app",
            "--reload",
            "--host", "127.0.0.1",
            "--port", "8000"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el servidor: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
