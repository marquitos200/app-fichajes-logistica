from sqlmodel import SQLModel, create_engine
from app.models import Company, User, ParteDia

# Recrear la base de datos con los nuevos campos
engine = create_engine('sqlite:///sqlite.db')

print("Recreando base de datos con nuevos campos...")
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
print("Base de datos actualizada correctamente!")
print("Nota: Se han perdido los datos anteriores. Deberás registrar una empresa nuevamente.")
