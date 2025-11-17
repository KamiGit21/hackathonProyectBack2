# app/repos/clientes_repo.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.firebase import get_firestore

COL = "clientes"

def _col():
    return get_firestore().collection(COL)

def _normalize_cliente(doc) -> Dict[str, Any]:
    d = doc.to_dict() or {}
    d["id"] = doc.id

    # Asegurar que fecha_alta sea string
    fa = d.get("fecha_alta")
    if isinstance(fa, (int, float)):
        # epoch -> fecha ISO (solo día)
        d["fecha_alta"] = datetime.fromtimestamp(fa, tz=timezone.utc).date().isoformat()
    elif isinstance(fa, datetime):
        d["fecha_alta"] = fa.date().isoformat()
    # si ya es string, lo dejamos tal cual, si no existe, queda None

    return d

def list_clientes() -> List[Dict[str, Any]]:
    out = []
    for doc in _col().stream():
        out.append(_normalize_cliente(doc))
    return out

def get_cliente(cliente_id: str) -> Optional[Dict[str, Any]]:
    snap = _col().document(cliente_id).get()
    if not snap.exists:
        return None
    return _normalize_cliente(snap)

def create_cliente(payload: Dict[str, Any]) -> Dict[str, Any]:
    # guardamos fecha_alta como string directamente
    now_str = datetime.utcnow().date().isoformat()
    data = {
        "nombre": payload["nombre"],
        "apellidos": payload.get("apellidos", ""),
        "ci_nit": payload.get("ci_nit"),
        "fecha_nacimiento": payload.get("fecha_nacimiento"),
        "email": payload["email"],
        "telefono": payload.get("telefono"),
        "direccion": payload.get("direccion"),
        "estado": payload.get("estado", "ACTIVO"),
        "fecha_alta": now_str,
    }
    doc_ref = _col().document()
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}

def update_cliente(cliente_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    doc_ref = _col().document(cliente_id)
    if not doc_ref.get().exists:
        return None
    data = {k: v for k, v in payload.items() if v is not None}
    if data:
        doc_ref.set(data, merge=True)
    return get_cliente(cliente_id)

def delete_cliente(cliente_id: str, hard: bool = False) -> bool:
    doc_ref = _col().document(cliente_id)
    snap = doc_ref.get()

    if not snap.exists:
        return False

    if hard:
        doc_ref.delete()
        return True

    # Borrado lógico
    doc_ref.set({"estado": "INACTIVO"}, merge=True)
    return True

