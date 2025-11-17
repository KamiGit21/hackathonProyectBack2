from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TipoCuenta(str, Enum):
    AHORRO = "AHORRO"
    CORRIENTE = "CORRIENTE"


class Moneda(str, Enum):
    BOB = "BOB"
    USD = "USD"


class EstadoCuenta(str, Enum):
    ACTIVA = "ACTIVA"
    BLOQUEADA = "BLOQUEADA"
    CERRADA = "CERRADA"


class TipoMovimiento(str, Enum):
    DEPOSITO = "DEPOSITO"
    RETIRO = "RETIRO"
    TRANSFERENCIA_ENTRADA = "TRANSFERENCIA_ENTRADA"
    TRANSFERENCIA_SALIDA = "TRANSFERENCIA_SALIDA"
    PAGO_SERVICIO = "PAGO_SERVICIO"


class Cuenta(BaseModel):
    id: Optional[str] = None
    cliente_id: str
    numero_cuenta: str
    tipo: TipoCuenta = TipoCuenta.AHORRO
    moneda: Moneda = Moneda.BOB
    saldo: float = 0.0
    estado: EstadoCuenta = EstadoCuenta.ACTIVA
    fecha_apertura: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class Movimiento(BaseModel):
    id: Optional[str] = None
    cuenta_id: str
    tipo: TipoMovimiento
    monto: float
    saldo_anterior: float
    saldo_nuevo: float
    descripcion: str
    referencia: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True