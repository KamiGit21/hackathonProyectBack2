from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TransferenciaBase(BaseModel):
    tipo: Literal["PROPIA", "TERCEROS", "INTERBANCARIA"]
    cuenta_origen_id: str
    monto: float = Field(..., gt=0)
    descripcion: Optional[str] = None

class TransferenciaPropiaTerceros(TransferenciaBase):
    cuenta_destino_id: str

class TransferenciaInterbancaria(TransferenciaBase):
    banco_destino: str
    nro_cuenta_externa: str

class Transferencia(TransferenciaBase):
    id: str
    cuenta_destino_id: Optional[str] = None
    banco_destino: Optional[str] = None
    nro_cuenta_externa: Optional[str] = None
    fecha: datetime
    estado: Literal["EXITOSA", "RECHAZADA"]

    class Config:
        from_attributes = True