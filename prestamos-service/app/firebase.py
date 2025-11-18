import firebase_admin
from firebase_admin import credentials, firestore
import os

# Ruta FIJA dentro del contenedor Docker
CREDENTIALS_PATH = "/app/secrets/prestamos-service-key.json"

# Validar que realmente exista
if not os.path.exists(CREDENTIALS_PATH):
    raise RuntimeError(f"⚠️ Archivo de credenciales NO encontrado en: {CREDENTIALS_PATH}")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# Cliente Firestore
db = firestore.client()
