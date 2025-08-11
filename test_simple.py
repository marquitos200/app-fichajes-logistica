import sys
import os

# Cambiar al directorio correcto
os.chdir(r"c:\Users\Administrador\Desktop\app_fichajes_logistica\app_fichajes_logistica")

try:
    from app.main import app
    print("✅ Aplicación importada exitosamente")
    
    # Verificar que los directorios existen
    import pathlib
    static_dir = pathlib.Path("static")
    templates_dir = pathlib.Path("templates")
    
    if static_dir.exists():
        print("✅ Directorio static encontrado")
    else:
        print("❌ Directorio static NO encontrado")
        
    if templates_dir.exists():
        print("✅ Directorio templates encontrado")
    else:
        print("❌ Directorio templates NO encontrado")
        
    print("\n🚀 La aplicación está lista para ejecutarse")
    print("💡 Ejecuta: uvicorn app.main:app --reload")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
