from fastapi import Depends, HTTPException, status
from google.cloud import firestore
from .firebase import get_firebase_app
from .security import get_current_user

def get_db() -> firestore.Client:
    app = get_firebase_app()
    return firestore.Client(project=app.project_id)

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user