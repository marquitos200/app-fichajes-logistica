from __future__ import annotations
from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, create_engine, Session, select, text
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import date, datetime
from pathlib import Path
import io, os
import pandas as pd
from typing import Optional

from .models import Company, User, ParteDia, ParteMensual, Ruta
from .auth import hash_password, verify_password, get_current_user, require_role

# Funciones de Flash Messages
def set_flash_message(request: Request, type: str, title: str, message: str):
    """Establece un mensaje flash en la sesión"""
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []
    request.session["flash_messages"].append({
        "type": type,
        "title": title,
        "message": message
    })

def get_flash_messages(request: Request):
    """Obtiene y limpia los mensajes flash de la sesión"""
    messages = request.session.get("flash_messages", [])
    request.session["flash_messages"] = []
    return messages

def flash_success(request: Request, title: str, message: str):
    """Mensaje flash de éxito"""
    set_flash_message(request, "success", title, message)

def flash_error(request: Request, title: str, message: str):
    """Mensaje flash de error"""
    set_flash_message(request, "error", title, message)

def flash_warning(request: Request, title: str, message: str):
    """Mensaje flash de advertencia"""
    set_flash_message(request, "warning", title, message)

def flash_info(request: Request, title: str, message: str):
    """Mensaje flash de información"""
    set_flash_message(request, "info", title, message)

# Obtener directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Configuración de base de datos para producción
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app_nueva.db")

# Para PostgreSQL en producción (Railway automáticamente provee DATABASE_URL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a False en producción
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def init_db():
    # Forzar recreación de todas las tablas
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

app = FastAPI(debug=True)

# Montar estáticos y plantillas
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def render_template(template_name: str, request: Request, **context):
    """Renderiza un template incluyendo mensajes flash"""
    context.update({
        "request": request,
        "flash_messages": get_flash_messages(request)
    })
    return templates.TemplateResponse(template_name, context)

# Crear tablas al arrancar
@app.on_event("startup")
def on_startup():
    init_db()

# Ruta simple para probar
@app.get("/health")
def health():
    return PlainTextResponse("ok")

# Middleware para adjuntar usuario a la request
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    with Session(engine) as db:
        user = get_current_user(request, db)
        request.state.user = user
        if user:
            # precargar company para usarla en plantillas
            company = db.get(Company, user.company_id)
            request.state.company = company
    response = await call_next(request)
    return response

# ⛳️ AÑADIR SESSION **DESPUÉS** DEL MIDDLEWARE HTTP PERSONALIZADO
app.add_middleware(SessionMiddleware, secret_key="cambia-esta-clave-super-larga")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.state.user:
        if request.state.user.role == "admin":
            return RedirectResponse("/admin", status_code=302)
        else:
            return RedirectResponse("/repartidor", status_code=302)
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return render_template("login.html", request, title="Login")

@app.post("/login")
def login_post(
    request: Request,
    company: str = Form(...),
    username: str = Form(...),
    password: str = Form(...)
):
    print(f"DEBUG: Intento de login - Empresa: {company}, Usuario: {username}")
    with Session(engine) as db:
        c = db.exec(select(Company).where(Company.name == company)).first()
        if not c:
            print(f"DEBUG: Empresa '{company}' no encontrada")
            flash_error(request, "Empresa no encontrada", f"La empresa '{company}' no existe en nuestro sistema.")
            return render_template("login.html", request, title="Login")
        print(f"DEBUG: Empresa encontrada - ID: {c.id}")
        
        u = db.exec(select(User).where(User.username == username, User.company_id == c.id)).first()
        if not u:
            print(f"DEBUG: Usuario '{username}' no encontrado en empresa {c.id}")
            flash_error(request, "Credenciales incorrectas", "El usuario o la contraseña son incorrectos.")
            return render_template("login.html", request, title="Login")
        print(f"DEBUG: Usuario encontrado - ID: {u.id}")
        
        if not verify_password(password, u.password_hash):
            print(f"DEBUG: Contraseña incorrecta para usuario {username}")
            flash_error(request, "Credenciales incorrectas", "El usuario o la contraseña son incorrectos.")
            return render_template("login.html", request, title="Login")
        
        print(f"DEBUG: Login exitoso para usuario {username}")
        request.session["user_id"] = u.id
        flash_success(request, "¡Bienvenido!", f"Has iniciado sesión correctamente como {u.role}.")
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    flash_info(request, "Sesión cerrada", "Has cerrado sesión correctamente. ¡Hasta la próxima!")
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return render_template("register.html", request, title="Registro")

@app.post("/register")
def register_post(
    request: Request,
    company: str = Form(None),
    company_key: str = Form(None),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("repartidor")
):
    with Session(engine) as db:
        # Verificar si el usuario ya existe
        existing_user = db.exec(select(User).where(User.username == username)).first()
        if existing_user:
            flash_error(request, "Usuario ya existe", f"El nombre de usuario '{username}' ya está en uso.")
            return render_template("register.html", request, title="Registro")
        
        if role == "admin":
            if not company:
                flash_error(request, "Datos incompletos", "Debes indicar el nombre de la empresa para crear una cuenta de administrador.")
                return render_template("register.html", request, title="Registro")
            
            exists = db.exec(select(Company).where(Company.name == company)).first()
            if exists:
                flash_error(request, "Empresa ya existe", f"La empresa '{company}' ya está registrada. Si eres repartidor, usa la opción de unirse con la clave de empresa.")
                return render_template("register.html", request, title="Registro")
            
            # Crear nueva empresa
            ckey = company_key or os.urandom(4).hex()
            comp = Company(name=company, company_key=ckey)
            db.add(comp); db.commit(); db.refresh(comp)
            
            # Crear usuario admin
            u = User(username=username, password_hash=hash_password(password), role="admin", company_id=comp.id)
            db.add(u); db.commit()
            
            flash_success(request, "¡Empresa creada!", f"Empresa '{company}' creada correctamente. Clave de empresa: {ckey}")
            
        else:  # repartidor
            if not company or not company_key:
                flash_error(request, "Datos incompletos", "Para registrarte como repartidor necesitas el nombre de la empresa y su clave de acceso.")
                return render_template("register.html", request, title="Registro")
            
            comp = db.exec(select(Company).where(Company.name == company)).first()
            if not comp:
                flash_error(request, "Empresa no encontrada", f"La empresa '{company}' no existe en nuestro sistema.")
                return render_template("register.html", request, title="Registro")
            
            if comp.company_key != company_key:
                flash_error(request, "Clave incorrecta", "La clave de empresa es incorrecta. Contacta con tu administrador.")
                return render_template("register.html", request, title="Registro")
            
            # Crear usuario repartidor
            u = User(username=username, password_hash=hash_password(password), role="repartidor", company_id=comp.id)
            db.add(u); db.commit()
            
            flash_success(request, "¡Registro exitoso!", f"Te has registrado correctamente en '{company}'. Ya puedes iniciar sesión.")
    
    return RedirectResponse("/login", status_code=302)

@app.get("/repartidor", response_class=HTMLResponse)
def repartidor_panel(request: Request, año: int | None = None, mes: int | None = None):
    from calendar import monthrange, Calendar
    
    with Session(engine) as db:
        user = require_role(request, db, "repartidor")
        today = date.today()
        
        # Usar año y mes actuales si no se especifican
        if not año:
            año = today.year
        if not mes:
            mes = today.month
            
        # Obtener primer y último día del mes
        primer_dia = date(año, mes, 1)
        ultimo_dia = date(año, mes, monthrange(año, mes)[1])
        
        # Obtener todos los partes del mes
        partes_mes = db.exec(
            select(ParteDia)
            .where(
                ParteDia.user_id == user.id,
                ParteDia.fecha >= primer_dia,
                ParteDia.fecha <= ultimo_dia,
            )
            .order_by(ParteDia.fecha)
        ).all()
        
        # Crear diccionario de partes por día (ahora puede haber múltiples partes por día)
        partes_por_dia = {}
        for p in partes_mes:
            dia = p.fecha.day
            if dia not in partes_por_dia:
                partes_por_dia[dia] = []
            partes_por_dia[dia].append(p)
        
        # Generar calendario del mes
        cal = Calendar(firstweekday=0)  # Lunes como primer día
        semanas = []
        for semana in cal.monthdayscalendar(año, mes):
            dias_semana = []
            for dia in semana:
                if dia == 0:
                    dias_semana.append(None)  # Día fuera del mes
                else:
                    fecha_dia = date(año, mes, dia)
                    partes_dia = partes_por_dia.get(dia, [])
                    
                    # Calcular totales del día para mostrar en el resumen
                    total_envios_dia = sum(p.num_envios or 0 for p in partes_dia)
                    total_km_dia = sum(p.km_diferencia or 0 for p in partes_dia)
                    total_gastos_dia = sum(
                        (p.dietas or 0) + (p.alojamiento or 0) + (p.transporte_billetes or 0) + 
                        (p.gasolina or 0) + (p.comida or 0) + (p.otros_consumiciones or 0) + 
                        (p.material or 0) + (p.otros_gastos or 0)
                        for p in partes_dia
                    )
                    
                    dias_semana.append({
                        'dia': dia,
                        'fecha': fecha_dia,
                        'partes': partes_dia,  # Lista de partes
                        'num_partes': len(partes_dia),
                        'total_envios': total_envios_dia,
                        'total_km': total_km_dia,
                        'total_gastos': total_gastos_dia,
                        'es_hoy': fecha_dia == today,
                        'es_pasado': fecha_dia < today,
                        'es_futuro': fecha_dia > today
                    })
            semanas.append(dias_semana)
        
        # Calcular estadísticas del mes
        total_km = sum(p.km_diferencia or 0 for p in partes_mes)
        total_horas = sum(p.horas or 0 for p in partes_mes)
        total_gastos = sum(
            (p.dietas or 0) + (p.alojamiento or 0) + (p.transporte_billetes or 0) + 
            (p.gasolina or 0) + (p.comida or 0) + (p.otros_consumiciones or 0) + 
            (p.material or 0) + (p.otros_gastos or 0)
            for p in partes_mes
        )
        dias_trabajados = len(partes_mes)
        
        # Verificar si existe parte mensual
        parte_mensual = db.exec(
            select(ParteMensual).where(
                ParteMensual.user_id == user.id,
                ParteMensual.año == año,
                ParteMensual.mes == mes
            )
        ).first()
        
        return render_template(
            "repartidor.html",
            request,
            title="Repartidor",
            año=año,
            mes=mes,
            semanas=semanas,
            partes_mes=partes_mes,
            total_km=total_km,
            total_horas=total_horas,
            total_gastos=total_gastos,
            dias_trabajados=dias_trabajados,
            parte_mensual=parte_mensual,
            meses=[
                (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
                (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
                (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
            ],
            años=list(range(today.year - 2, today.year + 2))
        )

@app.post("/repartidor/parte")
def guardar_parte(
    request: Request,
    fecha: str = Form(...),
    parte_id: str = Form(""),  # Cambiado a string para manejar cadenas vacías
    rutas_json: str = Form("[]"),  # JSON con las rutas
    # Kilómetros
    km_salida: float = Form(0.0),
    km_llegada: float = Form(0.0),
    km_diferencia: float = Form(0.0),
    repostaje: str = Form(None),
    num_factura: str = Form(None),
    # Gastos
    dietas: float = Form(0.0),
    alojamiento: float = Form(0.0),
    transporte_billetes: float = Form(0.0),
    km_recorridos: float = Form(0.0),
    gasolina: float = Form(0.0),
    comida: float = Form(0.0),
    otros_consumiciones: float = Form(0.0),
    material: float = Form(0.0),
    otros_gastos: float = Form(0.0),
    # Campos originales (ahora calculados)
    num_envios: int = Form(0),
    horas: float = Form(0.0),
    observaciones: str = Form(None),
):
    import json
    
    with Session(engine) as db:
        user = get_current_user(request, db)
        if not user:
            flash_error(request, "Acceso denegado", "Debes iniciar sesión para realizar esta acción.")
            return RedirectResponse("/login", status_code=302)
        
        # Solo admin y repartidores pueden crear/editar partes
        if user.role not in ["admin", "repartidor"]:
            flash_error(request, "Sin permisos", "No tienes permisos para crear o editar partes diarios.")
            return RedirectResponse("/", status_code=302)
        
        # Parsear rutas JSON
        try:
            rutas_data = json.loads(rutas_json) if rutas_json else []
        except json.JSONDecodeError:
            flash_error(request, "Error en rutas", "El formato de las rutas es inválido. Por favor, revisa los datos ingresados.")
            return RedirectResponse("/repartidor", status_code=302)
        
        # Convertir parte_id a entero si no está vacío
        parte_id_int = None
        if parte_id and parte_id.strip():
            try:
                parte_id_int = int(parte_id)
            except ValueError:
                flash_error(request, "Error en ID", "El identificador del parte es inválido.")
                return RedirectResponse("/repartidor", status_code=302)
        
        try:
            if parte_id_int:
                # Actualizar parte existente
                parte = db.get(ParteDia, parte_id_int)
                if not parte:
                    flash_error(request, "Parte no encontrado", "El parte que intentas editar no existe.")
                    return RedirectResponse("/repartidor", status_code=302)
                
                # Verificar permisos
                if user.role == "repartidor" and parte.user_id != user.id:
                    flash_error(request, "Sin permisos", "No puedes editar un parte que no te pertenece.")
                    return RedirectResponse("/repartidor", status_code=302)
                elif user.role == "admin" and parte.company_id != user.company_id:
                    flash_error(request, "Sin permisos", "No puedes editar un parte de otra empresa.")
                    return RedirectResponse("/repartidor", status_code=302)
                
                # Actualizar campos básicos del parte
                parte.km_salida = float(km_salida or 0)
                parte.km_llegada = float(km_llegada or 0)
                parte.km_diferencia = float(km_diferencia or 0)
                parte.repostaje = (repostaje or "").strip() or None
                parte.num_factura = (num_factura or "").strip() or None
                parte.observaciones = (observaciones or "").strip() or None
                parte.dietas = float(dietas or 0)
                parte.alojamiento = float(alojamiento or 0)
                parte.transporte_billetes = float(transporte_billetes or 0)
                parte.km_recorridos = float(km_recorridos or 0)
                parte.gasolina = float(gasolina or 0)
                parte.comida = float(comida or 0)
                parte.otros_consumiciones = float(otros_consumiciones or 0)
                parte.material = float(material or 0)
                parte.otros_gastos = float(otros_gastos or 0)
                parte.num_envios = int(num_envios or 0)
                parte.horas = float(horas or 0)
                
                # Eliminar rutas existentes y crear nuevas
                db.exec(text("DELETE FROM ruta WHERE parte_dia_id = :parte_id"), {"parte_id": parte_id_int})
                
                # Crear nuevas rutas
                for ruta_data in rutas_data:
                    nueva_ruta = Ruta(
                        parte_dia_id=parte_id_int,
                        orden=ruta_data.get('orden', 1),
                        descripcion=ruta_data.get('descripcion', '').strip() or None,
                        salida_lugar=ruta_data.get('salida_lugar', '').strip() or None,
                        salida_hora=ruta_data.get('salida_hora', '').strip() or None,
                        llegada_lugar=ruta_data.get('llegada_lugar', '').strip() or None,
                        llegada_hora=ruta_data.get('llegada_hora', '').strip() or None,
                        km_ruta=float(ruta_data.get('km_ruta', 0)),
                        num_envios_ruta=int(ruta_data.get('num_envios_ruta', 0)),
                        observaciones_ruta=ruta_data.get('observaciones_ruta', '').strip() or None
                    )
                    db.add(nueva_ruta)
                
                flash_success(request, "¡Parte actualizado!", f"El parte del {fecha} ha sido actualizado correctamente.")
                
            else:
                # Crear nuevo parte
                user_id_for_parte = user.id
                if user.role == "admin":
                    user_id_for_parte = user.id
                    
                p = ParteDia(
                    fecha=date.fromisoformat(fecha),
                    # Kilómetros
                    km_salida=float(km_salida or 0),
                    km_llegada=float(km_llegada or 0),
                    km_diferencia=float(km_diferencia or 0),
                    repostaje=(repostaje or "").strip() or None,
                    num_factura=(num_factura or "").strip() or None,
                    observaciones=(observaciones or "").strip() or None,
                    # Gastos
                    dietas=float(dietas or 0),
                    alojamiento=float(alojamiento or 0),
                    transporte_billetes=float(transporte_billetes or 0),
                    km_recorridos=float(km_recorridos or 0),
                    gasolina=float(gasolina or 0),
                    comida=float(comida or 0),
                    otros_consumiciones=float(otros_consumiciones or 0),
                    material=float(material or 0),
                    otros_gastos=float(otros_gastos or 0),
                    # Campos originales
                    num_envios=int(num_envios or 0),
                    horas=float(horas or 0),
                    # IDs
                    user_id=user_id_for_parte,
                    company_id=user.company_id,
                )
                db.add(p)
                db.commit()
                db.refresh(p)
                
                # Crear rutas asociadas al nuevo parte
                for ruta_data in rutas_data:
                    nueva_ruta = Ruta(
                        parte_dia_id=p.id,
                        orden=ruta_data.get('orden', 1),
                        descripcion=ruta_data.get('descripcion', '').strip() or None,
                        salida_lugar=ruta_data.get('salida_lugar', '').strip() or None,
                        salida_hora=ruta_data.get('salida_hora', '').strip() or None,
                        llegada_lugar=ruta_data.get('llegada_lugar', '').strip() or None,
                        llegada_hora=ruta_data.get('llegada_hora', '').strip() or None,
                        km_ruta=float(ruta_data.get('km_ruta', 0)),
                        num_envios_ruta=int(ruta_data.get('num_envios_ruta', 0)),
                        observaciones_ruta=ruta_data.get('observaciones_ruta', '').strip() or None
                    )
                    db.add(nueva_ruta)
                
                flash_success(request, "¡Parte creado!", f"El parte del {fecha} ha sido creado correctamente.")
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            flash_error(request, "Error al guardar", f"No se pudo guardar el parte: {str(e)}")
            
    return RedirectResponse("/repartidor", status_code=302)

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, user_id: str = "", desde: str | None = None, hasta: str | None = None):
    with Session(engine) as db:
        admin = require_role(request, db, "admin")
        company = db.get(Company, admin.company_id)
        users = db.exec(select(User).where(User.company_id == company.id, User.role == "repartidor")).all()
        
        # Convertir user_id a entero si no está vacío
        user_id_int = None
        if user_id and user_id.strip():
            try:
                user_id_int = int(user_id)
            except ValueError:
                user_id_int = None  # Si no es un entero válido, ignorar el filtro
        
        today = date.today()
        if not desde:
            desde = date(today.year, today.month, 1).isoformat()
        if not hasta:
            hasta = date(today.year, today.month, 28).isoformat()
            
        try:
            # Validar que las fechas sean válidas
            from datetime import datetime
            datetime.fromisoformat(desde)
            datetime.fromisoformat(hasta)
        except ValueError:
            # Si hay error en las fechas, usar fechas por defecto
            desde = date(today.year, today.month, 1).isoformat()
            hasta = date(today.year, today.month, 28).isoformat()
            
        q = (
            select(ParteDia, User)
            .where(
                ParteDia.company_id == company.id,
                ParteDia.fecha >= desde,
                ParteDia.fecha <= hasta,
            )
            .join(User, ParteDia.user_id == User.id)
        )
        if user_id_int:
            q = q.where(ParteDia.user_id == user_id_int)
        resultados = db.exec(q.order_by(ParteDia.fecha.desc())).all()
        
        # Crear lista de partes con información del usuario incluida
        partes_con_usuario = []
        for parte_dia, user_info in resultados:
            # Crear un objeto con toda la información necesaria
            parte_completo = {
                'id': parte_dia.id,
                'fecha': parte_dia.fecha,
                'username': user_info.username,
                'km_salida': parte_dia.km_salida,
                'km_llegada': parte_dia.km_llegada,
                'km_diferencia': parte_dia.km_diferencia,
                'salida_lugar': parte_dia.salida_lugar,
                'llegada_lugar': parte_dia.llegada_lugar,
                'horas': parte_dia.horas,
                'num_envios': parte_dia.num_envios,
                'dietas': parte_dia.dietas,
                'alojamiento': parte_dia.alojamiento,
                'transporte_billetes': parte_dia.transporte_billetes,
                'gasolina': parte_dia.gasolina,
                'comida': parte_dia.comida,
                'otros_consumiciones': parte_dia.otros_consumiciones,
                'material': parte_dia.material,
                'otros_gastos': parte_dia.otros_gastos,
                'observaciones': parte_dia.observaciones
            }
            partes_con_usuario.append(parte_completo)
        
        # Para cálculos, usar solo los objetos ParteDia
        partes_solo = [parte for parte, _ in resultados]
        
        # Calcular estadísticas
        total_km = sum((p.km_diferencia or 0) for p in partes_solo)
        total_horas = sum((p.horas or 0) for p in partes_solo)
        total_gastos = sum(
            (p.dietas or 0) + (p.alojamiento or 0) + (p.transporte_billetes or 0) + 
            (p.gasolina or 0) + (p.comida or 0) + (p.otros_consumiciones or 0) + 
            (p.material or 0) + (p.otros_gastos or 0)
            for p in partes_solo
        )
        
        # Estadísticas por usuario
        users_with_stats = []
        for user in users:
            user_partes = [p for p in partes_solo if p.user_id == user.id]
            user_km = sum((p.km_diferencia or 0) for p in user_partes)
            user_gastos = sum(
                (p.dietas or 0) + (p.alojamiento or 0) + (p.transporte_billetes or 0) + 
                (p.gasolina or 0) + (p.comida or 0) + (p.otros_consumiciones or 0) + 
                (p.material or 0) + (p.otros_gastos or 0)
                for p in user_partes
            )
            ultimo_parte = max([p.fecha for p in user_partes], default=None)
            users_with_stats.append({
                "id": user.id,
                "username": user.username,
                "partes_count": len(user_partes),
                "total_km": user_km,
                "total_gastos": user_gastos,
                "ultimo_parte": ultimo_parte.strftime('%d/%m/%Y') if ultimo_parte else 'Nunca'
            })
        
        # Comprobar si PDF está disponible
        try:
            import weasyprint  # type: ignore
            pdf_enabled = True
        except Exception:
            try:
                import reportlab  # type: ignore
                pdf_enabled = True
            except Exception:
                pdf_enabled = False
        return render_template(
            "admin.html",
            request,
            title="Admin",
            users=users_with_stats,
            partes=partes_con_usuario,
            company=company,
            selected_user=user_id_int,
            selected_user_str=user_id,  # Para el template
            desde=desde,
            hasta=hasta,
            pdf_enabled=pdf_enabled,
            total_km=total_km,
            total_horas=total_horas,
            total_gastos=total_gastos
        )

@app.get("/admin/export/excel")
def export_excel(request: Request, user_id: str = "", desde: str | None = None, hasta: str | None = None):
    with Session(engine) as db:
        admin = require_role(request, db, "admin")
        if not desde or not hasta:
            raise HTTPException(400, "Rango de fechas requerido")
        
        # Convertir user_id a entero si no está vacío
        user_id_int = None
        if user_id and user_id.strip():
            try:
                user_id_int = int(user_id)
            except ValueError:
                user_id_int = None
        
        try:
            # Validar formato de fechas
            from datetime import datetime
            datetime.fromisoformat(desde)
            datetime.fromisoformat(hasta)
        except ValueError:
            raise HTTPException(400, "Formato de fecha inválido. Use YYYY-MM-DD")
            
        q = (
            select(ParteDia, User)
            .where(
                ParteDia.company_id == admin.company_id,
                ParteDia.fecha >= desde,
                ParteDia.fecha <= hasta,
            )
            .join(User, ParteDia.user_id == User.id)
        )
        if user_id_int:
            q = q.where(ParteDia.user_id == user_id_int)
        rows = db.exec(q).all()
        
        data = []
        for p, u in rows:
            total_gastos = (
                (p.dietas or 0) + (p.alojamiento or 0) + (p.transporte_billetes or 0) + 
                (p.gasolina or 0) + (p.comida or 0) + (p.otros_consumiciones or 0) + 
                (p.material or 0) + (p.otros_gastos or 0)
            )
            data.append({
                "fecha": p.fecha.isoformat() if p.fecha else "",
                "repartidor": u.username,
                "km_salida": p.km_salida or 0,
                "km_llegada": p.km_llegada or 0,
                "km_diferencia": p.km_diferencia or 0,
                "salida_lugar": p.salida_lugar or "",
                "llegada_lugar": p.llegada_lugar or "",
                "horas": p.horas or 0,
                "num_envios": p.num_envios or 0,
                "dietas": p.dietas or 0,
                "gasolina": p.gasolina or 0,
                "alojamiento": p.alojamiento or 0,
                "comida": p.comida or 0,
                "material": p.material or 0,
                "otros_gastos": p.otros_gastos or 0,
                "total_gastos": total_gastos,
                "observaciones": p.observaciones or "",
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="partes_diarios")
        output.seek(0)
        filename = f"partes_{desde}_a_{hasta}" + (f"_user{user_id}" if user_id else "") + ".xlsx"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )

@app.get("/admin/export/pdf")
def export_pdf(request: Request, user_id: str = "", desde: str | None = None, hasta: str | None = None):
    with Session(engine) as db:
        admin = require_role(request, db, "admin")
        if not desde or not hasta:
            raise HTTPException(400, "Rango de fechas requerido")
            
        # Convertir user_id a entero si no está vacío
        user_id_int = None
        if user_id and user_id.strip():
            try:
                user_id_int = int(user_id)
            except ValueError:
                user_id_int = None
            
        try:
            # Validar formato de fechas
            from datetime import datetime
            datetime.fromisoformat(desde)
            datetime.fromisoformat(hasta)
        except ValueError:
            raise HTTPException(400, "Formato de fecha inválido. Use YYYY-MM-DD")
            
        q = (
            select(ParteDia, User)
            .where(
                ParteDia.company_id == admin.company_id,
                ParteDia.fecha >= desde,
                ParteDia.fecha <= hasta,
            )
            .join(User, ParteDia.user_id == User.id)
            .order_by(ParteDia.fecha)
        )
        if user_id_int:
            q = q.where(ParteDia.user_id == user_id_int)
        rows = db.exec(q).all()

        # HTML simple para exportar
        html = "<h2>Partes</h2><table border='1' cellspacing='0' cellpadding='4'><tr><th>Fecha</th><th>Usuario</th><th>Envíos</th><th>Km</th><th>Horas</th><th>Obs.</th></tr>"
        for p, u in rows:
            html += f"<tr><td>{p.fecha}</td><td>{u.username}</td><td>{p.num_envios}</td><td>{p.km}</td><td>{p.horas}</td><td>{p.observaciones or ''}</td></tr>"
        html += "</table>"

        # WeasyPrint si está disponible, si no ReportLab
        try:
            from weasyprint import HTML  # type: ignore
            pdf_bytes = HTML(string=html).write_pdf()
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="export.pdf"'},
            )
        except Exception:
            try:
                from reportlab.lib.pagesizes import A4  # type: ignore
                from reportlab.pdfgen import canvas  # type: ignore
                from reportlab.lib.units import mm  # type: ignore

                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                w, h = A4
                y = h - 20 * mm

                c.setFont("Helvetica-Bold", 14)
                c.drawString(20 * mm, y, "Partes")
                y -= 10 * mm

                c.setFont("Helvetica", 10)
                for p, u in rows:
                    line = f"{p.fecha} | {u.username} | {p.num_envios} env | {p.km} km | {p.horas} h | {p.observaciones or ''}"
                    c.drawString(20 * mm, y, line[:120])
                    y -= 6 * mm
                    if y < 20 * mm:
                        c.showPage()
                        y = h - 20 * mm

                c.showPage()
                c.save()
                buf.seek(0)
                return StreamingResponse(
                    buf,
                    media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="export.pdf"'},
                )
            except Exception:
                raise HTTPException(500, "Para exportar a PDF instala 'weasyprint' o 'reportlab'")

@app.post("/repartidor/parte-mensual")
def guardar_parte_mensual(
    request: Request,
    año: int = Form(...),
    mes: int = Form(...),
    observaciones_mes: str = Form(None),
):
    from datetime import datetime
    with Session(engine) as db:
        try:
            user = require_role(request, db, "repartidor")
            
            # Verificar si ya existe un parte mensual
            parte_existente = db.exec(
                select(ParteMensual).where(
                    ParteMensual.user_id == user.id,
                    ParteMensual.año == año,
                    ParteMensual.mes == mes
                )
            ).first()
            
            # Calcular totales automáticamente desde los partes diarios
            from calendar import monthrange
            primer_dia = date(año, mes, 1)
            ultimo_dia = date(año, mes, monthrange(año, mes)[1])
            
            partes_del_mes = db.exec(
                select(ParteDia).where(
                    ParteDia.user_id == user.id,
                    ParteDia.fecha >= primer_dia,
                    ParteDia.fecha <= ultimo_dia,
                )
            ).all()
            
            # Calcular totales
            total_dias = len(partes_del_mes)
            total_km = sum(p.km_diferencia or 0 for p in partes_del_mes)
            total_horas = sum(p.horas or 0 for p in partes_del_mes)
            total_envios = sum(p.num_envios or 0 for p in partes_del_mes)
            
            total_dietas = sum(p.dietas or 0 for p in partes_del_mes)
            total_alojamiento = sum(p.alojamiento or 0 for p in partes_del_mes)
            total_transporte = sum(p.transporte_billetes or 0 for p in partes_del_mes)
            total_gasolina = sum(p.gasolina or 0 for p in partes_del_mes)
            total_comida = sum(p.comida or 0 for p in partes_del_mes)
            total_material = sum(p.material or 0 for p in partes_del_mes)
            total_otros = sum(p.otros_gastos or 0 for p in partes_del_mes)
            
            nombre_mes = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][mes - 1]
            
            if parte_existente:
                # Actualizar
                parte_existente.total_dias_trabajados = total_dias
                parte_existente.total_km = total_km
                parte_existente.total_horas = total_horas
                parte_existente.total_envios = total_envios
                parte_existente.total_dietas = total_dietas
                parte_existente.total_alojamiento = total_alojamiento
                parte_existente.total_transporte = total_transporte
                parte_existente.total_gasolina = total_gasolina
                parte_existente.total_comida = total_comida
                parte_existente.total_material = total_material
                parte_existente.total_otros_gastos = total_otros
                parte_existente.observaciones_mes = (observaciones_mes or "").strip() or None
                parte_existente.fecha_actualizacion = datetime.now()
                
                flash_success(request, "¡Parte mensual actualizado!", f"El resumen de {nombre_mes} {año} ha sido actualizado correctamente.")
            else:
                # Crear nuevo
                pm = ParteMensual(
                    año=año,
                    mes=mes,
                    total_dias_trabajados=total_dias,
                    total_km=total_km,
                    total_horas=total_horas,
                    total_envios=total_envios,
                    total_dietas=total_dietas,
                    total_alojamiento=total_alojamiento,
                    total_transporte=total_transporte,
                    total_gasolina=total_gasolina,
                    total_comida=total_comida,
                    total_material=total_material,
                    total_otros_gastos=total_otros,
                    observaciones_mes=(observaciones_mes or "").strip() or None,
                    user_id=user.id,
                    company_id=user.company_id,
                )
                db.add(pm)
                
                flash_success(request, "¡Parte mensual creado!", f"El resumen de {nombre_mes} {año} ha sido creado correctamente con {total_dias} días trabajados.")
                
            db.commit()
            
        except Exception as e:
            db.rollback()
            flash_error(request, "Error al guardar", f"No se pudo guardar el parte mensual: {str(e)}")
            
    return RedirectResponse(f"/repartidor?año={año}&mes={mes}", status_code=302)

# API para obtener datos de un parte específico
@app.get("/api/parte/{parte_id}")
def get_parte_api(request: Request, parte_id: int):
    with Session(engine) as db:
        user = get_current_user(request, db)
        if not user:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener el parte
        parte = db.get(ParteDia, parte_id)
        if not parte:
            raise HTTPException(status_code=404, detail="Parte no encontrado")
        
        # Verificar permisos
        if user.role == "repartidor" and parte.user_id != user.id:
            raise HTTPException(status_code=403, detail="No puedes acceder a este parte")
        elif user.role == "admin" and parte.company_id != user.company_id:
            raise HTTPException(status_code=403, detail="No puedes acceder a este parte")
        
        return {
            "id": parte.id,
            "fecha": parte.fecha.isoformat(),
            "km_salida": parte.km_salida or 0,
            "km_llegada": parte.km_llegada or 0,
            "km_diferencia": parte.km_diferencia or 0,
            "repostaje": parte.repostaje or "",
            "num_factura": parte.num_factura or "",
            "salida_lugar": parte.salida_lugar or "",
            "salida_hora": parte.salida_hora or "",
            "llegada_lugar": parte.llegada_lugar or "",
            "llegada_hora": parte.llegada_hora or "",
            "tiempo_total": parte.tiempo_total or "",
            "observaciones": parte.observaciones or "",
            "dietas": parte.dietas or 0,
            "alojamiento": parte.alojamiento or 0,
            "transporte_billetes": parte.transporte_billetes or 0,
            "gasolina": parte.gasolina or 0,
            "comida": parte.comida or 0,
            "otros_consumiciones": parte.otros_consumiciones or 0,
            "material": parte.material or 0,
            "otros_gastos": parte.otros_gastos or 0,
            "num_envios": parte.num_envios or 0,
            "horas": parte.horas or 0,
        }

# Ruta para actualizar un parte existente
@app.put("/api/parte/{parte_id}")
def update_parte_api(
    request: Request,
    parte_id: int,
    # Kilómetros
    km_salida: float = Form(0.0),
    km_llegada: float = Form(0.0),
    km_diferencia: float = Form(0.0),
    repostaje: str = Form(None),
    num_factura: str = Form(None),
    # Rutas
    salida_lugar: str = Form(None),
    salida_hora: str = Form(None),
    llegada_lugar: str = Form(None),
    llegada_hora: str = Form(None),
    tiempo_total: str = Form(None),
    observaciones: str = Form(None),
    # Gastos
    dietas: float = Form(0.0),
    alojamiento: float = Form(0.0),
    transporte_billetes: float = Form(0.0),
    gasolina: float = Form(0.0),
    comida: float = Form(0.0),
    otros_consumiciones: float = Form(0.0),
    material: float = Form(0.0),
    otros_gastos: float = Form(0.0),
    # Campos originales
    num_envios: int = Form(0),
    horas: float = Form(0.0),
):
    with Session(engine) as db:
        user = get_current_user(request, db)
        if not user:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener el parte
        parte = db.get(ParteDia, parte_id)
        if not parte:
            raise HTTPException(status_code=404, detail="Parte no encontrado")
        
        # Verificar permisos
        if user.role == "repartidor" and parte.user_id != user.id:
            raise HTTPException(status_code=403, detail="No puedes editar este parte")
        elif user.role == "admin" and parte.company_id != user.company_id:
            raise HTTPException(status_code=403, detail="No puedes editar este parte")
        
        # Actualizar campos
        parte.km_salida = float(km_salida or 0)
        parte.km_llegada = float(km_llegada or 0)
        parte.km_diferencia = float(km_diferencia or 0)
        parte.repostaje = (repostaje or "").strip() or None
        parte.num_factura = (num_factura or "").strip() or None
        parte.salida_lugar = (salida_lugar or "").strip() or None
        parte.salida_hora = (salida_hora or "").strip() or None
        parte.llegada_lugar = (llegada_lugar or "").strip() or None
        parte.llegada_hora = (llegada_hora or "").strip() or None
        parte.tiempo_total = (tiempo_total or "").strip() or None
        parte.observaciones = (observaciones or "").strip() or None
        parte.dietas = float(dietas or 0)
        parte.alojamiento = float(alojamiento or 0)
        parte.transporte_billetes = float(transporte_billetes or 0)
        parte.gasolina = float(gasolina or 0)
        parte.comida = float(comida or 0)
        parte.otros_consumiciones = float(otros_consumiciones or 0)
        parte.material = float(material or 0)
        parte.otros_gastos = float(otros_gastos or 0)
        parte.num_envios = int(num_envios or 0)
        parte.horas = float(horas or 0)
        
        db.commit()
        return {"success": True}

# API para obtener múltiples partes de un día específico
@app.get("/api/partes-dia/{fecha_str}")
def get_partes_dia(fecha_str: str, request: Request):
    with Session(engine) as db:
        user = get_current_user(request, db)
        if not user:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")
        
        partes = db.exec(
            select(ParteDia)
            .where(
                ParteDia.user_id == user.id,
                ParteDia.fecha == fecha
            )
            .order_by(ParteDia.id)
        ).all()
        
        return [
            {
                "id": parte.id,
                "fecha": parte.fecha.strftime("%Y-%m-%d"),
                "salida_lugar": parte.salida_lugar,
                "salida_hora": parte.salida_hora,
                "llegada_lugar": parte.llegada_lugar,
                "llegada_hora": parte.llegada_hora,
                "km_diferencia": parte.km_diferencia,
                "num_envios": parte.num_envios,
                "horas": parte.horas,
                "dietas": parte.dietas,
                "alojamiento": parte.alojamiento,
                "transporte_billetes": parte.transporte_billetes,
                "gasolina": parte.gasolina,
                "comida": parte.comida,
                "otros_consumiciones": parte.otros_consumiciones,
                "material": parte.material,
                "otros_gastos": parte.otros_gastos,
                "observaciones": parte.observaciones
            }
            for parte in partes
        ]

# API para eliminar un parte específico
@app.delete("/api/parte/{parte_id}")
def eliminar_parte(parte_id: int, request: Request):
    with Session(engine) as db:
        user = get_current_user(request, db)
        if not user:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        parte = db.get(ParteDia, parte_id)
        if not parte:
            raise HTTPException(status_code=404, detail="Parte no encontrado")
        
        # Verificar permisos
        if user.role == "repartidor" and parte.user_id != user.id:
            raise HTTPException(status_code=403, detail="No puedes eliminar este parte")
        elif user.role == "admin" and parte.company_id != user.company_id:
            raise HTTPException(status_code=403, detail="No puedes eliminar este parte")
        
        db.delete(parte)
        db.commit()
        
        return {"message": "Parte eliminado correctamente"}
