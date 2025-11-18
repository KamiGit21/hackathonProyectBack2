from typing import Optional
from pydantic import BaseModel, Field


class PagoIn(BaseModel):
    cuenta_id: str
    tipo_servicio: str = Field(..., example="LUZ")
    referencia: str
    monto: float


class PagoOut(BaseModel):
    id: str
    cuenta_id: str
    tipo_servicio: str
    referencia: str
    monto: float
    fecha: int
    estado: str
    proveedor: Optional[str] = None
    mensaje_respuesta: Optional[str] = None
