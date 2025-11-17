import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

_firebase_app = None
_firestore_client = None


def init_firebase():
    global _firebase_app, _firestore_client

    cred_path_env = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    use_firestore = os.getenv("USE_FIRESTORE", "true").lower() != "false"

    if not cred_path_env:
        if use_firestore:
            raise RuntimeError("FIREBASE_CREDENTIALS_PATH not set and USE_FIRESTORE is true")
        return

    cred_path = Path(cred_path_env).expanduser().resolve()
    if not cred_path.is_file():
        raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")

    if _firebase_app is None:
        cred = credentials.Certificate(str(cred_path))
        _firebase_app = firebase_admin.initialize_app(cred)

    if use_firestore and _firestore_client is None:
        _firestore_client = firestore.client(app=_firebase_app)


def get_firestore():
    use_firestore = os.getenv("USE_FIRESTORE", "true").lower() != "false"
    if not use_firestore:
        return None
    if _firestore_client is None:
        init_firebase()
    return _firestore_client
