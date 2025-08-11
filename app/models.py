from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    pass

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    company_key: str  # clave privada que el admin comparte

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password_hash: str
    role: str = Field(index=True)  # 'admin' | 'repartidor'
    company_id: int = Field(foreign_key="company.id")

class ParteDia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date = Field(index=True)
    
    # Kilómetros
    km_salida: float = 0.0
    km_llegada: float = 0.0
    km_diferencia: float = 0.0
    repostaje: Optional[str] = None
    num_factura: Optional[str] = None
    
    # Viajes/Rutas
    salida_lugar: Optional[str] = None
    salida_hora: Optional[str] = None
    llegada_lugar: Optional[str] = None
    llegada_hora: Optional[str] = None
    tiempo_total: Optional[str] = None
    observaciones: Optional[str] = None
    
    # Gastos
    dietas: float = 0.0
    alojamiento: float = 0.0
    transporte_billetes: float = 0.0
    km_recorridos: float = 0.0
    gasolina: float = 0.0
    comida: float = 0.0
    otros_consumiciones: float = 0.0
    material: float = 0.0
    otros_gastos: float = 0.0
    
    # Campos originales (mantener compatibilidad)
    num_envios: int = 0
    km: float = 0.0
    horas: float = 0.0

    user_id: int = Field(foreign_key="user.id")
    company_id: int = Field(foreign_key="company.id")

class ParteMensual(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    año: int = Field(index=True)
    mes: int = Field(index=True)  # 1-12
    
    # Totales del mes
    total_dias_trabajados: int = 0
    total_km: float = 0.0
    total_horas: float = 0.0
    total_envios: int = 0
    
    # Totales de gastos
    total_dietas: float = 0.0
    total_alojamiento: float = 0.0
    total_transporte: float = 0.0
    total_gasolina: float = 0.0
    total_comida: float = 0.0
    total_material: float = 0.0
    total_otros_gastos: float = 0.0
    
    # Observaciones del mes
    observaciones_mes: Optional[str] = None
    
    # Fechas de creación/actualización
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    
    user_id: int = Field(foreign_key="user.id")
    company_id: int = Field(foreign_key="company.id")

class Ruta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parte_dia_id: int = Field(foreign_key="partedia.id")
    
    # Información de la ruta
    orden: int = 1  # Para ordenar las rutas del día
    descripcion: Optional[str] = None  # Descripción de la ruta
    salida_lugar: Optional[str] = None
    salida_hora: Optional[str] = None
    llegada_lugar: Optional[str] = None
    llegada_hora: Optional[str] = None
    km_ruta: float = 0.0
    num_envios_ruta: int = 0
    observaciones_ruta: Optional[str] = None

class FotoEntrega(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ruta_id: int = Field(foreign_key="ruta.id")
    nombre_archivo: str  # nombre del archivo en el sistema
    nombre_original: str  # nombre original del archivo
    descripcion: Optional[str] = None  # descripción de la foto
    fecha_subida: datetime = Field(default_factory=datetime.now)
    tamaño_bytes: int = 0
