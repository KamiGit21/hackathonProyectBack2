from fastapi import FastAPI
from .routers import transferencias
from .firebase import get_firebase_app

app = FastAPI(title="Transferencias Service")

get_firebase_app()  # Initialize Firebase

app.include_router(transferencias.router, prefix="/api/transferencias")