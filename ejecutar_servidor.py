import os
import sys
import uvicorn

# Cambiar al directorio del proyecto
os.chdir('C:/Users/Administrador/Desktop/app_fichajes_logistica/app_fichajes_logistica')

print("🚀 Iniciando servidor FastAPI...")
print("📍 Directorio de trabajo:", os.getcwd())
print("🌐 Servidor disponible en: http://127.0.0.1:8000")
print("📋 Para acceder al panel de administración: http://127.0.0.1:8000/admin")
print("👤 Para acceder al panel de repartidor: http://127.0.0.1:8000/repartidor")
print("🔑 Primero debes registrarte en: http://127.0.0.1:8000/register")
print("\n" + "="*60)

# Ejecutar el servidor
uvicorn.run('app.main:app', host='127.0.0.1', port=8000, reload=True)
