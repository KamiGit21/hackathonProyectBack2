from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PrestamoCreate(BaseModel):
    cliente_id: str
    monto: float
    plazo_meses: int
    tasa_anual: float

class PrestamoUpdate(BaseModel):
    estado: str

class PrestamoResponse(BaseModel):
    id: str
    cliente_id: str
    monto: float
    plazo_meses: int
    tasa_anual: float
    estado: str
    fecha_solicitud: datetime
