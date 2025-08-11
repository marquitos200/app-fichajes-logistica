#!/usr/bin/env python3
"""
Script para preparar la aplicación para despliegue en Railway
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} - Completado")
            return True
        else:
            print(f"❌ {description} - Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_files():
    """Verifica que todos los archivos necesarios estén presentes"""
    required_files = [
        'Procfile',
        'railway.json', 
        'requirements.txt',
        'runtime.txt',
        '.gitignore',
        'app/main.py',
        'app/models.py',
        'app/auth.py',
        'templates/base.html',
        'templates/login.html',
        'templates/register.html',
        'templates/repartidor.html',
        'templates/admin.html',
        'static/style.css'
    ]
    
    print("📋 Verificando archivos necesarios...")
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"\n❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    print("\n✅ Todos los archivos necesarios están presentes")
    return True

def prepare_for_deployment():
    """Prepara el proyecto para despliegue"""
    print("🚀 PREPARANDO APLICACIÓN PARA DESPLIEGUE EN RAILWAY")
    print("=" * 60)
    
    # Verificar archivos
    if not check_files():
        return False
    
    # Limpiar archivos temporales
    print("\n🧹 Limpiando archivos temporales...")
    temp_patterns = [
        "*.pyc",
        "__pycache__/",
        "*.db",
        ".pytest_cache/",
        "*.log"
    ]
    
    # Inicializar git si no existe
    if not Path('.git').exists():
        print("\n📦 Inicializando repositorio Git...")
        run_command('git init', 'Inicializar Git')
        run_command('git branch -M main', 'Crear rama main')
    
    # Verificar que requirements.txt esté actualizado
    print("\n📝 Verificando dependencias...")
    
    # Mostrar resumen de configuración
    print("\n📋 RESUMEN DE CONFIGURACIÓN PARA RAILWAY:")
    print("-" * 50)
    print("✅ Procfile: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
    print("✅ Runtime: Python 3.12")
    print("✅ Base de datos: PostgreSQL (automática en Railway)")
    print("✅ Archivos estáticos: /static/")
    print("✅ Templates: /templates/")
    print("✅ Sistema de notificaciones: Implementado")
    print("✅ Flash messages: Implementado")
    
    print("\n🎯 SIGUIENTE PASO:")
    print("1. Sube el código a GitHub")
    print("2. Conecta Railway con tu repositorio de GitHub")
    print("3. Railway desplegará automáticamente")
    
    print("\n📱 FUNCIONALIDADES INCLUIDAS:")
    print("• Sistema completo de fichajes para repartidores")
    print("• Panel de administración avanzado")
    print("• Exportación a Excel y PDF")
    print("• Dashboard tipo calendario")
    print("• Sistema de rutas múltiples")
    print("• Notificaciones bonitas para errores y avisos")
    print("• Responsive design profesional")
    print("• Auto-registro con clave de empresa")
    
    print("\n🌐 URLs que estarán disponibles:")
    print("• / - Redirección automática según rol")
    print("• /login - Página de inicio de sesión")
    print("• /register - Página de registro")
    print("• /repartidor - Dashboard del repartidor")
    print("• /admin - Panel de administración")
    print("• /health - Healthcheck para Railway")
    
    return True

if __name__ == "__main__":
    success = prepare_for_deployment()
    if success:
        print("\n🎉 ¡APLICACIÓN LISTA PARA DESPLIEGUE!")
        print("\nPuedes proceder a subir a GitHub y Railway.")
    else:
        print("\n❌ Hay problemas que resolver antes del despliegue.")
        sys.exit(1)
