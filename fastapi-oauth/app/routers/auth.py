# app/routers/auth.py
from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.responses import RedirectResponse
import urllib.parse
from app.config import settings
from app.security import create_access_token
from app.schemas import TokenOut, MeOut, StaffOut, UserOut, AuthUser
from app.firebase import get_auth
from app.repos.users_repo import (
    create_or_update_from_google,
    get_user_doc,
)
from app.deps import current_user  # valida tu JWT y carga usuario desde Firestore

router = APIRouter(prefix="/auth", tags=["auth"])

# ──────────────────────────────────────────────────────────────────────────────
# OAuth cliente (Google)
# ──────────────────────────────────────────────────────────────────────────────
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ──────────────────────────────────────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/google/login")
async def google_login(request: Request):
    """
    Inicia el flujo de OAuth en Google (redirección al consentimiento).
    """
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    # --- IGUAL QUE ANTES: flujo OAuth ---
    try:
        token = await oauth.google.authorize_access_token(request)

        userinfo = None
        if token and "id_token" in token:
            try:
                userinfo = await oauth.google.parse_id_token(request, token)
            except Exception:
                userinfo = None

        if not userinfo:
            userinfo_endpoint = oauth.google.server_metadata.get(
                "userinfo_endpoint",
                "https://openidconnect.googleapis.com/v1/userinfo"
            )
            resp = await oauth.google.get(userinfo_endpoint, token=token)
            data = resp.json()
            userinfo = {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name"),
                "given_name": data.get("given_name") or (data.get("name") or "").split(" ")[0],
                "family_name": data.get("family_name"),
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified"),
            }

        if not userinfo.get("sub"):
            raise HTTPException(status_code=400, detail="Google userinfo sin 'sub'")

    except OAuthError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": e.error, "description": e.description}
        )

    # --- Firebase Auth ---
    fb_auth = get_auth()
    uid = userinfo["sub"]

    try:
        fb_auth.get_user(uid)
        fb_auth.update_user(
            uid=uid,
            email=userinfo.get("email"),
            email_verified=bool(userinfo.get("email_verified")),
            display_name=userinfo.get("name"),
            photo_url=userinfo.get("picture"),
            disabled=False,
        )
    except Exception:
        fb_auth.create_user(
            uid=uid,
            email=userinfo.get("email"),
            email_verified=bool(userinfo.get("email_verified")),
            display_name=userinfo.get("name"),
            photo_url=userinfo.get("picture"),
            disabled=False,
        )

    # --- Firestore: upsert ---
    user_out = create_or_update_from_google(userinfo, uid)
    doc = get_user_doc(uid) or {}
    roles = doc.get("roles", ["ADMIN"])

    # --- JWT ---
    access = create_access_token({
        "sub": uid,
        "email": userinfo.get("email"),
        "roles": roles
    })

    # -----------------------------
    # 🔥 REDIRECCIÓN AL FRONT
    # -----------------------------
    FRONTEND_URL = "http://localhost:3000"  #por el momento jiji

    params = urllib.parse.urlencode({
        "token": access,
        "roles": ",".join(roles),
        "email": userinfo.get("email")
    })

    redirect_url = f"{FRONTEND_URL}/callback?{params}"
    return RedirectResponse(url=redirect_url) 

@router.get("/me", response_model=StaffOut)
def me(user: AuthUser = Depends(current_user)):
    """
    Devuelve el perfil del usuario autenticado (según tu JWT + Firestore).
    Transforma AuthUser -> StaffOut para cumplir el response_model.
    """
    doc = get_user_doc(user.uid) or {}
    username = (
        doc.get("username") or
        ((doc.get("email") or "").split("@")[0][:16] if doc.get("email") else "user")
    )

    return UserOut(
        uid=user.uid,
        first_name=doc.get("given_name"),
        last_name=doc.get("family_name"),
        email=doc.get("email"),
        username=username,
        active=bool(doc.get("active", True)),
        last_update=None,  # opcional: mapear updated_at epoch -> datetime si quieres
        roles=user.roles
    )

@router.post("/logout")
def logout():
    """
    Endpoint de logout.
    
    Para JWT real no hay 'logout' en el servidor, solo confirmamos
    que el cliente debe borrar su token local.
    """
    return {"ok": True, "message": "Sesión cerrada. Por favor elimina tu JWT."}
