from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..schemas import Transferencia, TransferenciaPropiaTerceros, TransferenciaInterbancaria
from ..services.transferencias_service import TransferenciasService
from ..deps import get_db, get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Transferencia])
def list_transferencias(
    cuenta_id: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    service = TransferenciasService(db)
    return service.get_all(cuenta_id, tipo, current_user["uid"])

@router.get("/{transferencia_id}", response_model=Transferencia)
def get_transferencia(
    transferencia_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    service = TransferenciasService(db)
    transferencia = service.get_by_id(transferencia_id, current_user["uid"])
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferencia not found")
    return transferencia

@router.post("/", response_model=Transferencia)
async def create_transferencia(
    body: dict,  # Handle union manually
    db = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    service = TransferenciasService(db)
    try:
        if body["tipo"] in ["PROPIA", "TERCEROS"]:
            validated = TransferenciaPropiaTerceros(**body)
        elif body["tipo"] == "INTERBANCARIA":
            validated = TransferenciaInterbancaria(**body)
        else:
            raise ValueError("Invalid tipo")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    return await service.create(validated.dict(), current_user["uid"])