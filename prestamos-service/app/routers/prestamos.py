from fastapi import APIRouter, HTTPException
from app.schemas import PrestamoCreate, PrestamoUpdate, PrestamoResponse
from app.firebase import db
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/prestamos", tags=["Prestamos"])


# GET lista de préstamos
@router.get("/", response_model=list[PrestamoResponse])
def listar_prestamos(cliente_id: str = None, estado: str = None):

    prestamos_ref = db.collection("prestamos")
    query = prestamos_ref

    if cliente_id:
        query = query.where("cliente_id", "==", cliente_id)

    if estado:
        query = query.where("estado", "==", estado)

    docs = query.stream()

    resultados = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        resultados.append(PrestamoResponse(**data))

    return resultados


# GET préstamo por ID
@router.get("/{prestamo_id}", response_model=PrestamoResponse)
def obtener_prestamo(prestamo_id: str):
    doc = db.collection("prestamos").document(prestamo_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    data = doc.to_dict()
    data["id"] = doc.id
    return PrestamoResponse(**data)


# POST crear préstamo
@router.post("/", response_model=PrestamoResponse)
def crear_prestamo(data: PrestamoCreate):

    prestamo_id = uuid.uuid4().hex

    # Regla simple de aprobación
    estado = "APROBADO" if data.monto <= 20000 else "EN_EVALUACION"

    payload = {
        "cliente_id": data.cliente_id,
        "monto": data.monto,
        "plazo_meses": data.plazo_meses,
        "tasa_anual": data.tasa_anual,
        "estado": estado,
        "fecha_solicitud": datetime.utcnow()
    }

    db.collection("prestamos").document(prestamo_id).set(payload)

    payload["id"] = prestamo_id
    return PrestamoResponse(**payload)


# PUT actualizar préstamo
@router.put("/{prestamo_id}", response_model=PrestamoResponse)
def actualizar_prestamo(prestamo_id: str, data: PrestamoUpdate):

    doc_ref = db.collection("prestamos").document(prestamo_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    doc_ref.update({"estado": data.estado})

    updated = doc_ref.get().to_dict()
    updated["id"] = prestamo_id

    return PrestamoResponse(**updated)
