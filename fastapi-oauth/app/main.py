# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.firebase import init_firebase
from app.routers import auth as auth_router
from app.routers import auth_roles
from app.routers import clientes as clientes_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_firebase()
    except Exception as e:
        print(f"[WARN] Firebase init skipped/failed: {e}")
    yield

app = FastAPI(
    title="CHUNO Auth & Clientes Service",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=False,
)

allowed_origins = settings.cors_origins or ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(auth_roles.router)
app.include_router(clientes_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
