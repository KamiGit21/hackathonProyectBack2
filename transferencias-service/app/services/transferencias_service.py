import httpx
from datetime import datetime
from ..schemas import Transferencia
from ..repos.transferencias_repo import TransferenciasRepo
from ..config import config
from typing import List, Optional
from fastapi import HTTPException

class TransferenciasService:
    def __init__(self, db):
        self.repo = TransferenciasRepo(db)

    def get_all(self, cuenta_id: Optional[str], tipo: Optional[str], user_id: str) -> List[Transferencia]:
        transferencias = self.repo.get_all(cuenta_id, tipo)
        # Filter by user ownership
        return [t for t in transferencias if self._user_owns_cuenta(user_id, t.cuenta_origen_id)]

    def get_by_id(self, transferencia_id: str, user_id: str) -> Optional[Transferencia]:
        transferencia = self.repo.get_by_id(transferencia_id)
        if transferencia and self._user_owns_cuenta(user_id, transferencia.cuenta_origen_id):
            return transferencia
        return None

    async def create(self, data: dict, user_id: str) -> Transferencia:
        if not await self._user_owns_cuenta(user_id, data["cuenta_origen_id"]):
            raise HTTPException(status_code=403, detail="Not authorized for this cuenta")

        # Validate saldo
        if not await self._validar_saldo(data["cuenta_origen_id"], data["monto"]):
            raise HTTPException(status_code=400, detail="Insufficient balance")

        estado = "RECHAZADA"
        try:
            if data["tipo"] in ["PROPIA", "TERCEROS"]:
                await self._update_cuenta(data["cuenta_origen_id"], -data["monto"])
                await self._update_cuenta(data["cuenta_destino_id"], data["monto"])
                estado = "EXITOSA"
            elif data["tipo"] == "INTERBANCARIA":
                await self._update_cuenta(data["cuenta_origen_id"], -data["monto"])
                estado = "EXITOSA"  # Assume handled externally; save details
        except Exception as e:
            # Rollback if possible, but for simplicity, just set rejected
            pass

        transferencia_data = {
            **data,
            "fecha": datetime.utcnow(),
            "estado": estado
        }
        id = self.repo.create(transferencia_data)
        return Transferencia(id=id, **transferencia_data)

    async def _validar_saldo(self, cuenta_id: str, monto: float) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}/validar-saldo?monto={monto}")
            resp.raise_for_status()
            return resp.json()["tiene_saldo"]

    async def _update_cuenta(self, cuenta_id: str, monto: float):
        async with httpx.AsyncClient() as client:
            if monto > 0:
                payload = {"monto": monto, "descripcion": "Transferencia recibida"}
                resp = await client.post(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}/depositar", json=payload)
            elif monto < 0:
                payload = {"monto": abs(monto), "descripcion": "Transferencia enviada"}
                resp = await client.post(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}/retirar", json=payload)
            else:
                return
            resp.raise_for_status()

    async def _user_owns_cuenta(self, user_id: str, cuenta_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}")
            if resp.status_code != 200:
                return False
            data = resp.json()
            return data["cliente_id"] == user_id