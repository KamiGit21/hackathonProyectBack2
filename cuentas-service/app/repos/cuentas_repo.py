from typing import List, Optional
from datetime import datetime
from firebase_admin import firestore
from models import Cuenta, Movimiento, EstadoCuenta
from schemas import CuentaFilter, MovimientoFilter
import random
import string


class CuentasRepository:
    def __init__(self, db):
        self.db = db
        self.collection = "cuentas"
        self.movimientos_collection = "movimientos"

    def _generar_numero_cuenta(self) -> str:
        """Genera un número de cuenta único de 10 dígitos"""
        return ''.join(random.choices(string.digits, k=10))

    def _cuenta_existe(self, numero_cuenta: str) -> bool:
        """Verifica si un número de cuenta ya existe"""
        docs = self.db.collection(self.collection).where(
            "numero_cuenta", "==", numero_cuenta
        ).limit(1).stream()
        return len(list(docs)) > 0

    def _generar_numero_cuenta_unico(self) -> str:
        """Genera un número de cuenta único"""
        while True:
            numero = self._generar_numero_cuenta()
            if not self._cuenta_existe(numero):
                return numero

    def create(self, cuenta: Cuenta) -> str:
        """Crea una nueva cuenta"""
        cuenta.numero_cuenta = self._generar_numero_cuenta_unico()
        cuenta.created_at = datetime.now()
        cuenta.updated_at = datetime.now()
        
        cuenta_dict = cuenta.model_dump(exclude={"id"})
        cuenta_dict["fecha_apertura"] = cuenta.fecha_apertura
        cuenta_dict["created_at"] = cuenta.created_at
        cuenta_dict["updated_at"] = cuenta.updated_at
        
        doc_ref = self.db.collection(self.collection).add(cuenta_dict)
        return doc_ref[1].id

    def get_by_id(self, cuenta_id: str) -> Optional[Cuenta]:
        """Obtiene una cuenta por ID"""
        doc = self.db.collection(self.collection).document(cuenta_id).get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        data["id"] = doc.id
        return Cuenta(**data)

    def get_by_numero_cuenta(self, numero_cuenta: str) -> Optional[Cuenta]:
        """Obtiene una cuenta por número de cuenta"""
        docs = self.db.collection(self.collection).where(
            "numero_cuenta", "==", numero_cuenta
        ).limit(1).stream()
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            return Cuenta(**data)
        
        return None

    def list(self, filters: Optional[CuentaFilter] = None) -> List[Cuenta]:
        """Lista cuentas con filtros opcionales"""
        query = self.db.collection(self.collection)
        
        if filters:
            if filters.cliente_id:
                query = query.where("cliente_id", "==", filters.cliente_id)
            if filters.numero_cuenta:
                query = query.where("numero_cuenta", "==", filters.numero_cuenta)
            if filters.estado:
                query = query.where("estado", "==", filters.estado.value)
            if filters.moneda:
                query = query.where("moneda", "==", filters.moneda.value)
        
        docs = query.stream()
        cuentas = []
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            cuentas.append(Cuenta(**data))
        
        return cuentas

    def update(self, cuenta_id: str, update_data: dict) -> bool:
        """Actualiza una cuenta"""
        update_data["updated_at"] = datetime.now()
        
        doc_ref = self.db.collection(self.collection).document(cuenta_id)
        doc_ref.update(update_data)
        return True

    def update_saldo(self, cuenta_id: str, nuevo_saldo: float) -> bool:
        """Actualiza el saldo de una cuenta"""
        return self.update(cuenta_id, {"saldo": nuevo_saldo})

    def cambiar_estado(self, cuenta_id: str, nuevo_estado: EstadoCuenta) -> bool:
        """Cambia el estado de una cuenta"""
        return self.update(cuenta_id, {"estado": nuevo_estado.value})

    def delete(self, cuenta_id: str) -> bool:
        """Elimina una cuenta (soft delete)"""
        return self.cambiar_estado(cuenta_id, EstadoCuenta.CERRADA)

    # Métodos para movimientos
    def crear_movimiento(self, movimiento: Movimiento) -> str:
        """Crea un registro de movimiento"""
        movimiento.created_at = datetime.now()
        
        movimiento_dict = movimiento.model_dump(exclude={"id"})
        movimiento_dict["fecha"] = movimiento.fecha
        movimiento_dict["created_at"] = movimiento.created_at
        
        doc_ref = self.db.collection(self.movimientos_collection).add(movimiento_dict)
        return doc_ref[1].id

    def get_movimientos(
        self, 
        cuenta_id: str, 
        filters: Optional[MovimientoFilter] = None,
        limit: int = 50
    ) -> List[Movimiento]:
        """Obtiene los movimientos de una cuenta"""
        query = self.db.collection(self.movimientos_collection).where(
            "cuenta_id", "==", cuenta_id
        ).order_by("fecha", direction=firestore.Query.DESCENDING).limit(limit)
        
        if filters:
            if filters.tipo:
                query = query.where("tipo", "==", filters.tipo.value)
            if filters.fecha_desde:
                query = query.where("fecha", ">=", filters.fecha_desde)
            if filters.fecha_hasta:
                query = query.where("fecha", "<=", filters.fecha_hasta)
        
        docs = query.stream()
        movimientos = []
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            movimientos.append(Movimiento(**data))
        
        return movimientos