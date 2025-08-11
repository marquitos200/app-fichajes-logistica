@echo off
echo ========================================
echo    SISTEMA DE FICHAJES LOGISTICA
echo ========================================
echo.
echo Iniciando servidor FastAPI...
echo.
cd /d "C:\Users\Administrador\Desktop\app_fichajes_logistica\app_fichajes_logistica"
echo Directorio actual: %CD%
echo.
echo Servidor disponible en:
echo   http://127.0.0.1:8000
echo.
echo Paginas principales:
echo   - Registro:      http://127.0.0.1:8000/register
echo   - Login:         http://127.0.0.1:8000/login  
echo   - Repartidor:    http://127.0.0.1:8000/repartidor
echo   - Admin:         http://127.0.0.1:8000/admin
echo.
echo ========================================
echo.
"C:\Users\Administrador\Desktop\app_fichajes_logistica\.venv\Scripts\uvicorn.exe" app.main:app --reload --host 127.0.0.1 --port 8000
pause
