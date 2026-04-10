"""
CRUD de técnicos del taller del usuario autenticado (rol TALLER).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import TALLERES, TECNICOS, USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_taller
from app.presentation.api.v1.schemas.technician import (
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
)

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])


def _taller_del_token(db: Session, usuario: USUARIOS) -> TALLERES:
    """Resuelve el taller único asociado al usuario con rol TALLER."""
    t = db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()
    if not t:
        raise HTTPException(
            status_code=400,
            detail="Debe registrar su taller antes de gestionar técnicos",
        )
    return t


def _tecnico_en_taller(
    db: Session,
    id_tecnico: UUID,
    id_taller: UUID,
) -> TECNICOS | None:
    return (
        db.query(TECNICOS)
        .filter(TECNICOS.ID_TECNICO == id_tecnico, TECNICOS.ID_TALLER == id_taller)
        .first()
    )


@router.get("", response_model=list[TechnicianResponse])
def listar_tecnicos(
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Lista los técnicos del taller del usuario autenticado."""
    taller = _taller_del_token(db, dueno)
    items = (
        db.query(TECNICOS)
        .filter(TECNICOS.ID_TALLER == taller.ID_TALLER)
        .order_by(TECNICOS.NOMBRE_COMPLETO)
        .all()
    )
    return [TechnicianResponse.model_validate(x) for x in items]


@router.post("", response_model=TechnicianResponse, status_code=status.HTTP_201_CREATED)
def crear_tecnico(
    datos: TechnicianCreate,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Alta de técnico en el taller del usuario."""
    taller = _taller_del_token(db, dueno)
    tecnico = TECNICOS(
        ID_TALLER=taller.ID_TALLER,
        NOMBRE_COMPLETO=datos.nombre_completo,
        TELEFONO=datos.telefono,
        DISPONIBLE=datos.disponible,
    )
    db.add(tecnico)
    db.commit()
    db.refresh(tecnico)
    return TechnicianResponse.model_validate(tecnico)


@router.get("/{id_tecnico}", response_model=TechnicianResponse)
def obtener_tecnico(
    id_tecnico: UUID,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Detalle de un técnico del propio taller."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return TechnicianResponse.model_validate(t)


@router.put("/{id_tecnico}", response_model=TechnicianResponse)
def actualizar_tecnico(
    id_tecnico: UUID,
    datos: TechnicianUpdate,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Actualiza datos del técnico."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    if datos.nombre_completo is not None:
        t.NOMBRE_COMPLETO = datos.nombre_completo
    if datos.telefono is not None:
        t.TELEFONO = datos.telefono
    if datos.disponible is not None:
        t.DISPONIBLE = datos.disponible

    db.add(t)
    db.commit()
    db.refresh(t)
    return TechnicianResponse.model_validate(t)


@router.delete("/{id_tecnico}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tecnico(
    id_tecnico: UUID,
    db: Session = Depends(get_db),
    dueno: USUARIOS = Depends(get_current_taller),
):
    """Elimina un técnico del taller."""
    taller = _taller_del_token(db, dueno)
    t = _tecnico_en_taller(db, id_tecnico, taller.ID_TALLER)
    if not t:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    db.delete(t)
    db.commit()
    return None
