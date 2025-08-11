from sqlmodel import create_engine, Session
from app.models import Company, User
from app.auth import hash_password

engine = create_engine('sqlite:///sqlite.db')

# Datos de ejemplo
empresas_ejemplo = [
    {
        "name": "Transportes García",
        "company_key": "garcia123",
        "admin": {"username": "admin", "password": "admin123"},
        "repartidores": [
            {"username": "carlos", "password": "carlos123"},
            {"username": "maria", "password": "maria123"},
            {"username": "jose", "password": "jose123"}
        ]
    },
    {
        "name": "Logística Madrid",
        "company_key": "madrid456",
        "admin": {"username": "director", "password": "director123"},
        "repartidores": [
            {"username": "ana", "password": "ana123"},
            {"username": "pedro", "password": "pedro123"}
        ]
    },
    {
        "name": "Express Delivery",
        "company_key": "express789",
        "admin": {"username": "jefe", "password": "jefe123"},
        "repartidores": [
            {"username": "luis", "password": "luis123"},
            {"username": "sara", "password": "sara123"},
            {"username": "miguel", "password": "miguel123"},
            {"username": "laura", "password": "laura123"}
        ]
    }
]

print("🚀 Creando usuarios de ejemplo...")

with Session(engine) as db:
    for empresa_data in empresas_ejemplo:
        print(f"\n📊 Empresa: {empresa_data['name']}")
        
        # Crear empresa
        company = Company(
            name=empresa_data["name"],
            company_key=empresa_data["company_key"]
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Crear admin
        admin_data = empresa_data["admin"]
        admin = User(
            username=admin_data["username"],
            password_hash=hash_password(admin_data["password"]),
            role="admin",
            company_id=company.id
        )
        db.add(admin)
        print(f"  👨‍💼 Admin: {admin_data['username']} / {admin_data['password']}")
        
        # Crear repartidores
        for rep_data in empresa_data["repartidores"]:
            repartidor = User(
                username=rep_data["username"],
                password_hash=hash_password(rep_data["password"]),
                role="repartidor",
                company_id=company.id
            )
            db.add(repartidor)
            print(f"  🚛 Repartidor: {rep_data['username']} / {rep_data['password']}")
        
        db.commit()

print("\n✅ Usuarios de ejemplo creados correctamente!")
print("\n🔑 DATOS PARA LOGIN:")
print("=" * 50)

for empresa_data in empresas_ejemplo:
    print(f"\n🏢 EMPRESA: {empresa_data['name']}")
    print(f"   Clave empresa: {empresa_data['company_key']}")
    print(f"   👨‍💼 Admin: {empresa_data['admin']['username']} / {empresa_data['admin']['password']}")
    for rep in empresa_data['repartidores']:
        print(f"   🚛 Repartidor: {rep['username']} / {rep['password']}")

print("\n" + "=" * 50)
print("💡 Para hacer login, usa:")
print("   - Empresa: [nombre de la empresa]")
print("   - Usuario: [username]")
print("   - Contraseña: [password]")
