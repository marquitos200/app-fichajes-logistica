import os, sys
import uvicorn
# Ya estamos en el directorio correcto, no necesitamos agregar más al path
from app.main import app  # <- nuestra FastAPI

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
