# app/schemas_clientes.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class ClienteCreate(BaseModel):
    nombre: str
    apellidos: str
    ci_nit: Optional[str] = None           # 👈 puede venir vacío desde el front
    fecha_nacimiento: Optional[str] = None # "YYYY-MM-DD"
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    ci_nit: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None

class ClienteOut(BaseModel):
    id: str
    nombre: str
    apellidos: Optional[str] = None
    ci_nit: Optional[str] = None               # 👈 ahora opcional
    fecha_nacimiento: Optional[str] = None
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Literal["ACTIVO", "INACTIVO"]
    fecha_alta: Optional[str] = None           # 👈 la convertiremos a string en el repo
