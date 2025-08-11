from __future__ import annotations
from fastapi import Request, HTTPException
from passlib.hash import bcrypt
from sqlmodel import Session, select
from .models import User, Company
from typing import Optional

SESSION_KEY = "user_id"

def hash_password(pw:str)->str:
    return bcrypt.hash(pw)

def verify_password(pw:str, pw_hash:str)->bool:
    return bcrypt.verify(pw, pw_hash)

def get_current_user(request: Request, db: Session) -> Optional[User]:
    uid = request.session.get(SESSION_KEY)
    print(f"DEBUG get_current_user: user_id en session={uid}")
    if not uid:
        print(f"DEBUG get_current_user: No hay user_id en session")
        return None
    u = db.get(User, uid)
    print(f"DEBUG get_current_user: Usuario encontrado={u}")
    return u

def require_role(request: Request, db: Session, role: str):
    u = get_current_user(request, db)
    print(f"DEBUG require_role: Usuario={u}, Rol requerido={role}")
    if u:
        print(f"DEBUG require_role: Rol del usuario={u.role}")
    if not u or u.role != role:
        print(f"DEBUG require_role: Acceso denegado")
        raise HTTPException(status_code=403, detail="No autorizado")
    print(f"DEBUG require_role: Acceso permitido")
    return u
