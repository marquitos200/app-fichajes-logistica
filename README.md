# 🚚 App de Fichajes Logística

Sistema de gestión de partes diarios para empresas de logística y reparto.

## 🌟 Características

- ✅ Gestión de múltiples repartidores por empresa
- 📋 Creación de partes diarios con múltiples rutas
- 📊 Dashboard administrativo con estadísticas
- 📅 Vista calendario mensual para repartidores
- 💰 Control de gastos por categorías
- 📈 Exportación a Excel y PDF
- 🎨 Interfaz moderna y responsive

## 🚀 Despliegue en Railway

### 1. Subir a GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Desplegar en Railway

1. Ve a [railway.app](https://railway.app)
2. Conecta tu cuenta de GitHub
3. Haz clic en "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repositorio
5. Railway detectará automáticamente que es una app Python
6. Se desplegará automáticamente

### 3. Configurar Base de Datos

1. En el dashboard de Railway, haz clic en "Add Service" → "Database" → "PostgreSQL"
2. Railway automáticamente configurará la variable `DATABASE_URL`
3. La app se conectará automáticamente a PostgreSQL

### 4. Acceder a la Aplicación

- Railway te dará una URL como: `https://tu-app.railway.app`
- **Credenciales iniciales:**
  - Usuario: `admin`
  - Contraseña: `admin123`
  - Clave empresa: `DEMO2025`

## 🆔 Credenciales por Defecto

**⚠️ IMPORTANTE: Cambia estas credenciales en producción**

- **Admin**: admin / admin123
- **Clave empresa**: DEMO2025

## 🔄 Actualizaciones

Para actualizar la aplicación:

```bash
git add .
git commit -m "Update"
git push
```

Railway se redesplegará automáticamente.

## 📞 Soporte

Sistema desarrollado para gestión de fichajes logísticos.
¡Listo para usar en producción! 🚀

## Ejecutar
```bash
uvicorn app.main:app --reload
```
Abre http://127.0.0.1:8000

## Notas
- Este es un punto de partida. Ajusta campos/validaciones a tu Excel real.
- Seguridad básica con sesiones firmadas y contraseñas hasheadas (bcrypt).
- Todo queda **local** en `sqlite.db`.
