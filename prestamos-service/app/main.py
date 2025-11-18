from fastapi import FastAPI
from app.routers import prestamos

app = FastAPI(
    title="prestamos-service",
    version="1.0"
)

app.include_router(prestamos.router)


@app.get("/")
def root():
    return {"mensaje": "prestamos-service funcionando con Firestore 🚀"}
