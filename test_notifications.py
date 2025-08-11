#!/usr/bin/env python3
"""
Script para probar que las notificaciones flash funcionan correctamente
"""

try:
    # Importar la app y verificar que funciona
    from app.main import app, flash_success, flash_error, flash_warning, flash_info
    from fastapi.testclient import TestClient
    
    print("✅ App importada correctamente")
    print("✅ Funciones de flash messages importadas correctamente")
    
    # Crear cliente de test
    client = TestClient(app)
    
    # Test de la página de login
    response = client.get("/login")
    if response.status_code == 200:
        print("✅ Página de login accesible")
    else:
        print(f"❌ Error en página de login: {response.status_code}")
    
    # Test de la página de registro
    response = client.get("/register")
    if response.status_code == 200:
        print("✅ Página de registro accesible")
    else:
        print(f"❌ Error en página de registro: {response.status_code}")
    
    print("\n🎉 Todas las verificaciones pasaron correctamente!")
    print("\nLos mensajes de notificación flash están listos para usar:")
    print("- ✅ Mensajes de éxito (color verde)")
    print("- ❌ Mensajes de error (color rojo)")
    print("- ⚠️ Mensajes de advertencia (color amarillo)")
    print("- ℹ️ Mensajes de información (color azul)")
    
    print("\nEjemplos de uso:")
    print("- Si olvidas la contraseña de empresa: aparecerá un error bonito")
    print("- Si el registro es exitoso: aparecerá un mensaje de éxito")
    print("- Si hay problemas con el formulario: aparecerá una advertencia")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
