import time
import uuid
import random
from typing import Optional

import requests
from fastapi import APIRouter, HTTPException, status

from app.schemas import PagoIn, PagoOut
from app.firebase import get_firestore

router = APIRouter()


def _pagos_col():
    fs = get_firestore()
    if fs is None:
        raise RuntimeError("Firestore no disponible")
    return fs.collection("pagos")


def _simulate_provider_call(pago: dict) -> tuple[bool, str]:
    # Simula llamada a proveedor externo: 90% éxito
    ok = random.random() < 0.9
    if ok:
        return True, "Proveedor: pago aceptado"
    return False, "Proveedor: pago rechazado"


def _call_accounts_service(cuenta_id: str, monto: float) -> tuple[bool, str]:
    """
    Llama a cuentas-service para retirar saldo.
    Si CUENTAS_SERVICE_URL no está definida, usa simulación.
    """
    if not CUENTAS_SERVICE_URL:
        # Simulación: aprobar pagos <= 1000, fallar pagos > 1000
        if monto <= 1000:
            return True, "Simulación: cuenta debitada"
        return False, "Simulación: saldo insuficiente"

    url = f"{CUENTAS_SERVICE_URL}/api/cuentas/{cuenta_id}/retirar"
    payload = {"monto": monto}
    try:
        resp = requests.post(url, json=payload, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") or data.get("charged"):
                return True, "Cuenta debitada"
            return False, data.get("message", "Saldo insuficiente")
        if resp.status_code == 402:
            return False, "Saldo insuficiente"
        return False, f"Cuentas-service respuesta: {resp.status_code}"
    except requests.RequestException as e:
        # Si falla la conexión, simula
        if monto <= 1000:
            return True, "Simulación: cuenta debitada"
        return False, f"Simulación: error conexión ({str(e)})"


@router.get("/api/pagos", response_model=list[PagoOut])
def list_pagos(cuenta_id: Optional[str] = None, tipo_servicio: Optional[str] = None):
    col = _pagos_col()
    query = col
    if cuenta_id:
        query = query.where("cuenta_id", "==", cuenta_id)
    if tipo_servicio:
        query = query.where("tipo_servicio", "==", tipo_servicio)
    docs = query.stream()
    out = []
    for d in docs:
        data = d.to_dict() or {}
        out.append(PagoOut(**data))
    return out


@router.get("/api/pagos/{pago_id}", response_model=PagoOut)
def get_pago(pago_id: str):
    doc = _pagos_col().document(pago_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    data = doc.to_dict() or {}
    return PagoOut(**data)


@router.post("/api/pagos", response_model=PagoOut, status_code=status.HTTP_201_CREATED)
def create_pago(payload: PagoIn):
    # 1) Llamar a cuentas-service para validar y descontar
    ok_c, msg_c = _call_accounts_service(payload.cuenta_id, payload.monto)

    now = int(time.time())
    pago_id = uuid.uuid4().hex
    base_doc = {
        "id": pago_id,
        "cuenta_id": payload.cuenta_id,
        "tipo_servicio": payload.tipo_servicio,
        "referencia": payload.referencia,
        "monto": payload.monto,
        "fecha": now,
    }

    if not ok_c:
        # Guardar como FALLIDO por falta de fondos
        doc = {**base_doc, "estado": "FALLIDO", "proveedor": None, "mensaje_respuesta": f"Cuentas: {msg_c}"}
        _pagos_col().document(pago_id).set(doc)
        raise HTTPException(status_code=402, detail={"error": "saldo_insuficiente", "mensaje": msg_c})

    # 2) Simular llamada a proveedor
    ok_p, msg_p = _simulate_provider_call(base_doc)
    estado = "EXITOSO" if ok_p else "FALLIDO"

    doc = {**base_doc, "estado": estado, "proveedor": "SIMULADO", "mensaje_respuesta": msg_p}
    _pagos_col().document(pago_id).set(doc)

    return PagoOut(**doc)
