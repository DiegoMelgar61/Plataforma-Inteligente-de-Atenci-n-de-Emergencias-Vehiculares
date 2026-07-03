"""
CRUD de vehículos del cliente autenticado.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import USUARIOS, VEHICULOS
from app.modules.auth.dependencies import get_current_cliente
from app.presentation.api.v1.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


def _vehiculo_de_cliente(
    db: Session,
    id_vehiculo: UUID,
    id_cliente: UUID,
) -> VEHICULOS | None:
    return (
        db.query(VEHICULOS)
        .filter(
            VEHICULOS.ID_VEHICULO == id_vehiculo,
            VEHICULOS.ID_USUARIO_CLIENTE == id_cliente,
        )
        .first()
    )


@router.get("", response_model=list[VehicleResponse])
def listar_mis_vehiculos(
    db: Session = Depends(get_db),
    cliente: USUARIOS = Depends(get_current_cliente),
):
    """Lista todos los vehículos registrados por el cliente."""
    items = (
        db.query(VEHICULOS)
        .filter(VEHICULOS.ID_USUARIO_CLIENTE == cliente.ID_USUARIO)
        .order_by(VEHICULOS.FECHA_CREACION.desc())
        .all()
    )
    return [VehicleResponse.model_validate(v) for v in items]


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(
    datos: VehicleCreate,
    db: Session = Depends(get_db),
    cliente: USUARIOS = Depends(get_current_cliente),
):
    """Registra un vehículo asociado al cliente autenticado."""
    if datos.placa:
        existe = db.query(VEHICULOS).filter(VEHICULOS.PLACA == datos.placa).first()
        if existe:
            raise HTTPException(status_code=400, detail="La placa ya está registrada")

    vehiculo = VEHICULOS(
        ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
        MARCA=datos.marca,
        MODELO=datos.modelo,
        ANIO=datos.anio,
        PLACA=datos.placa,
    )
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return VehicleResponse.model_validate(vehiculo)


@router.get("/{id_vehiculo}", response_model=VehicleResponse)
def obtener_vehiculo(
    id_vehiculo: UUID,
    db: Session = Depends(get_db),
    cliente: USUARIOS = Depends(get_current_cliente),
):
    """Detalle de un vehículo propio."""
    v = _vehiculo_de_cliente(db, id_vehiculo, cliente.ID_USUARIO)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return VehicleResponse.model_validate(v)


@router.put("/{id_vehiculo}", response_model=VehicleResponse)
def actualizar_vehiculo(
    id_vehiculo: UUID,
    datos: VehicleUpdate,
    db: Session = Depends(get_db),
    cliente: USUARIOS = Depends(get_current_cliente),
):
    """Actualiza datos del vehículo (solo el propietario)."""
    v = _vehiculo_de_cliente(db, id_vehiculo, cliente.ID_USUARIO)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if datos.placa is not None and datos.placa != v.PLACA:
        existe = (
            db.query(VEHICULOS)
            .filter(VEHICULOS.PLACA == datos.placa, VEHICULOS.ID_VEHICULO != id_vehiculo)
            .first()
        )
        if existe:
            raise HTTPException(status_code=400, detail="La placa ya está en uso")

    if datos.marca is not None:
        v.MARCA = datos.marca
    if datos.modelo is not None:
        v.MODELO = datos.modelo
    if datos.anio is not None:
        v.ANIO = datos.anio
    if datos.placa is not None:
        v.PLACA = datos.placa

    db.add(v)
    db.commit()
    db.refresh(v)
    return VehicleResponse.model_validate(v)


@router.delete("/{id_vehiculo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(
    id_vehiculo: UUID,
    db: Session = Depends(get_db),
    cliente: USUARIOS = Depends(get_current_cliente),
):
    """Elimina un vehículo del cliente."""
    v = _vehiculo_de_cliente(db, id_vehiculo, cliente.ID_USUARIO)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    db.delete(v)
    db.commit()
    return None
