REM ====================================================================
REM COMANDOS PARA SUBIR LA APP A GITHUB Y RAILWAY
REM ====================================================================

REM Navegar al directorio del proyecto
cd "c:\Users\Administrador\Desktop\app_fichajes_logistica\app_fichajes_logistica"

REM Agregar todos los archivos al repositorio Git
git add .

REM Hacer commit con mensaje descriptivo
git commit -m "🚀 App de fichajes logísticos lista para producción con notificaciones bonitas"

REM ====================================================================
REM DESPUÉS DE CREAR EL REPOSITORIO EN GITHUB, EJECUTAR:
REM ====================================================================

REM Conectar con GitHub (reemplaza 'TU-USUARIO' con tu usuario real)
git remote add origin https://github.com/TU-USUARIO/app-fichajes-logistica.git

REM Subir el código a GitHub
git push -u origin main

REM ====================================================================
REM LISTO! Ahora ve a railway.app y despliega desde GitHub
REM ====================================================================
