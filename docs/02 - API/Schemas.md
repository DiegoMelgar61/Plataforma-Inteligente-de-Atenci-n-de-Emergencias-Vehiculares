---
titulo: "Schemas Pydantic"
tipo: API
fecha: 2026-07-03
tags: [schemas, pydantic, request, response]
---

# Schemas Pydantic

## Auth

```python
class UserCreate(BaseModel):
    correo_electronico: str
    contrasena: str
    nombre_completo: str
    telefono: str | None = None

class UserLogin(BaseModel):
    correo_electronico: str
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

## Users

```python
class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_usuario: int
    correo_electronico: str
    nombre_completo: str
    telefono: str | None
    rol: str
    activo: bool
    fecha_creacion: datetime

class UserUpdate(BaseModel):
    nombre_completo: str | None = None
    telefono: str | None = None
```

## Workshops

```python
class WorkshopCreate(BaseModel):
    nombre_negocio: str
    nit: str | None = None
    direccion: str | None = None
    tasa_comision: Decimal | None = Decimal("10.00")
    latitud: Decimal | None = None
    longitud: Decimal | None = None

class WorkshopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_taller: int
    nombre_negocio: str
    nit: str | None
    # ... otros campos
```

## Technicians

```python
class TechnicianCreate(BaseModel):
    nombre_completo: str
    telefono: str | None = None
    disponible: bool = True

class TechnicianWithUserCreate(TechnicianCreate):
    correo_electronico: str
    contrasena: str
    id_taller: int | None = None
```

## Incidents

```python
class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_incidente: int
    estado: str
    prioridad: str
    clasificacion: str
    resumen_ia: str | None
    latitud: float | None
    longitud: float | None
    evidencias: list[EvidenceItemResponse]
    # ... campos de asignación

class ReporteIncidenteResponse(BaseModel):
    incidente_id: int
    evidencias_subidas: list[EvidenceUploadResponse]
```

## Assignments

```python
class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_asignacion: int
    id_incidente: int
    id_taller: int
    id_tecnico: int | None

class CotizacionCreate(BaseModel):
    monto_cotizado: Decimal
    tiempo_estimado_reparacion: int | None = None
    notas_cotizacion: str | None = None

class CotizacionRespuesta(BaseModel):
    aceptada: bool
    motivo_rechazo: str | None = None
```

## Payments

```python
class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_pago: int
    monto: Decimal
    comision_plataforma: Decimal
    estado: str
    metodo_pago: str | None

class PaymentReject(BaseModel):
    motivo_rechazo: str
```

## Documentos Relacionados

- [[Endpoints]]
- [[Modelo de Datos]]
