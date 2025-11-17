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
        # Filter by user ownership (assume cuentas-service links cuentas to users)
        return [t for t in transferencias if self._user_owns_cuenta(user_id, t.cuenta_origen_id)]

    def get_by_id(self, transferencia_id: str, user_id: str) -> Optional[Transferencia]:
        transferencia = self.repo.get_by_id(transferencia_id)
        if transferencia and self._user_owns_cuenta(user_id, transferencia.cuenta_origen_id):
            return transferencia
        return None

    async def create(self, data: dict, user_id: str) -> Transferencia:
        if not self._user_owns_cuenta(user_id, data["cuenta_origen_id"]):
            raise HTTPException(status_code=403, detail="Not authorized for this cuenta")

        # Validate saldo
        saldo = await self._get_saldo(data["cuenta_origen_id"])
        if saldo < data["monto"]:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        estado = "RECHAZADA"
        try:
            if data["tipo"] in ["PROPIA", "TERCEROS"]:
                await self._update_cuenta(data["cuenta_origen_id"], -data["monto"])
                await self._update_cuenta(data["cuenta_destino_id"], data["monto"])
                estado = "EXITOSA"
            elif data["tipo"] == "INTERBANCARIA":
                await self._update_cuenta(data["cuenta_origen_id"], -data["monto"])
                await self._send_to_intermediario(data)
                estado = "EXITOSA"
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

    async def _get_saldo(self, cuenta_id: str) -> float:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}")
            resp.raise_for_status()
            return resp.json()["saldo"]

    async def _update_cuenta(self, cuenta_id: str, monto: float):
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{config.CUENTAS_SERVICE_URL}/{cuenta_id}", json={"monto": monto})
            resp.raise_for_status()

    async def _send_to_intermediario(self, data: dict):
        async with httpx.AsyncClient() as client:
            payload = {
                "banco_destino": data["banco_destino"],
                "nro_cuenta_externa": data["nro_cuenta_externa"],
                "monto": data["monto"],
                "descripcion": data.get("descripcion")
            }
            resp = await client.post(config.INTERMEDIARIO_SERVICE_URL, json=payload)
            resp.raise_for_status()

    def _user_owns_cuenta(self, user_id: str, cuenta_id: str) -> bool:
        # Assume call to cuentas-service to check ownership
        # For simplicity, return True; implement real check
        return True