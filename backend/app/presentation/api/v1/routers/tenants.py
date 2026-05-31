from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.use_cases import tenant_service
from app.core.database import get_db
from app.models.models import USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_admin
from app.presentation.api.v1.schemas.tenants import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantResponse])
def listar_tenants(
    solo_activos: bool = False,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_admin),
):
    return tenant_service.obtener_tenants(db, solo_activos=solo_activos)


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def crear_tenant(
    datos: TenantCreate,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_admin),
):
    return tenant_service.crear_tenant(db, datos)


@router.get("/{id_tenant}", response_model=TenantResponse)
def obtener_tenant(
    id_tenant: UUID,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_admin),
):
    return tenant_service.obtener_tenant_por_id(db, id_tenant)


@router.patch("/{id_tenant}", response_model=TenantResponse)
def actualizar_tenant(
    id_tenant: UUID,
    datos: TenantUpdate,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_admin),
):
    return tenant_service.actualizar_tenant(db, id_tenant, datos)


@router.patch("/{id_tenant}/toggle-activo", response_model=TenantResponse)
def toggle_activo_tenant(
    id_tenant: UUID,
    db: Session = Depends(get_db),
    _: USUARIOS = Depends(get_current_admin),
):
    tenant = tenant_service.obtener_tenant_por_id(db, id_tenant)
    return tenant_service.actualizar_tenant(
        db,
        id_tenant,
        TenantUpdate(activo=not tenant.ACTIVO),
    )
