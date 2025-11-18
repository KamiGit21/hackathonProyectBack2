import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "secrets/auth/transferencias-service-credentials.json")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "transferenciaschuno")
    USE_FIRESTORE = os.getenv("USE_FIRESTORE", "true").lower() == "true"
    FIRESTORE_TRANSFERENCIAS_COLLECTION = os.getenv("FIRESTORE_TRANSFERENCIAS_COLLECTION", "transferencias")
    CUENTAS_SERVICE_URL = os.getenv("CUENTAS_SERVICE_URL", "http://cuentas-service:8003/api/cuentas")

config = Config()