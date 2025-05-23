from fastapi import FastAPI
from database import Base, engine

app = FastAPI()

# Crear las tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "¡MVP Mañaneras conectado a PostgreSQL!"}
