import firebase_admin
from firebase_admin import credentials, firestore
import os

# Ruta del archivo JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "prestamos-service-key.json")

cred = credentials.Certificate(KEY_PATH)

firebase_admin.initialize_app(cred)

db = firestore.client()
