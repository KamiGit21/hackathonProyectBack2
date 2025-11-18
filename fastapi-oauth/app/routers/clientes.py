# app/routers/clientes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas_clientes import ClienteCreate, ClienteUpdate, ClienteOut
from app.repos import clientes_repo as repo
from app.authz import require_roles, Role

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("", response_model=List[ClienteOut])
def list_clientes():
    return repo.list_clientes()

@router.get("/{cliente_id}", response_model=ClienteOut)
def get_cliente(cliente_id: str):
    c = repo.get_cliente(cliente_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c

@router.post("", response_model=ClienteOut,
             dependencies=[Depends(require_roles(Role.ADMIN))])
def create_cliente(payload: ClienteCreate):
    return repo.create_cliente(payload.model_dump())

@router.patch("/{cliente_id}", response_model=ClienteOut,
              dependencies=[Depends(require_roles(Role.ADMIN))])
def update_cliente(cliente_id: str, payload: ClienteUpdate):
    c = repo.update_cliente(cliente_id, payload.model_dump())
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c

@router.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: str, hard: bool = False):
    ok = repo.delete_cliente(cliente_id, hard)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"ok": True, "hard": hard}

