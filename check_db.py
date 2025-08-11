from sqlmodel import create_engine, Session, select
from app.models import Company, User, ParteDia

engine = create_engine('sqlite:///sqlite.db')

with Session(engine) as db:
    companies = db.exec(select(Company)).all()
    users = db.exec(select(User)).all()
    
    print(f"Total empresas: {len(companies)}")
    print(f"Total usuarios: {len(users)}")
    
    if companies:
        print("\nEmpresas registradas:")
        for c in companies:
            print(f"- {c.name} (ID: {c.id})")
    
    if users:
        print("\nUsuarios registrados:")
        for u in users:
            print(f"- {u.username} (rol: {u.role}, empresa_id: {u.company_id})")
    
    if not companies and not users:
        print("\nNo hay datos en la base de datos. Necesitas registrar una empresa primero.")
