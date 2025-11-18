from google.cloud import firestore
from ..schemas import Transferencia
from ..config import config
from typing import List, Optional

class TransferenciasRepo:
    def __init__(self, db: firestore.Client):
        self.collection = db.collection(config.FIRESTORE_TRANSFERENCIAS_COLLECTION)

    def get_all(self, cuenta_id: Optional[str] = None, tipo: Optional[str] = None) -> List[Transferencia]:
        query = self.collection
        if cuenta_id:
            # Firestore requires union queries for OR
            # Use two queries and combine results
            origen_query = self.collection.where("cuenta_origen_id", "==", cuenta_id)
            destino_query = self.collection.where("cuenta_destino_id", "==", cuenta_id)
            docs = list(origen_query.stream()) + list(destino_query.stream())
            # Dedup if needed, but rare
            transferencias = {doc.id: Transferencia(**doc.to_dict(), id=doc.id) for doc in docs}.values()
        else:
            docs = query.stream()
            transferencias = [Transferencia(**doc.to_dict(), id=doc.id) for doc in docs]
        if tipo:
            transferencias = [t for t in transferencias if t.tipo == tipo]
        return list(transferencias)

    def get_by_id(self, transferencia_id: str) -> Optional[Transferencia]:
        doc = self.collection.document(transferencia_id).get()
        if doc.exists:
            return Transferencia(**doc.to_dict(), id=doc.id)
        return None

    def create(self, data: dict) -> str:
        _, doc_ref = self.collection.add(data)
        return doc_ref.id

    def update(self, transferencia_id: str, data: dict):
        self.collection.document(transferencia_id).update(data)