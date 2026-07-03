from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import USUARIOS
from app.modules.bitacora import service as bitacora_service
from app.modules.tenants import service as tenant_service
from app.modules.tenants.schemas import TenantCreate, TenantResponse, TenantUpdate
from app.presentation.api.v1.dependencies.auth import get_current_admin

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
    usuario: USUARIOS = Depends(get_current_admin),
):
    tenant = tenant_service.crear_tenant(db, datos)
    bitacora_service.registrar(
        "TENANT_CREADO",
        f"Admin creó el tenant '{tenant.NOMBRE}'",
        usuario=usuario,
        entidad="TENANT",
        id_entidad=tenant.ID_TENANT,
    )
    return tenant


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
    usuario: USUARIOS = Depends(get_current_admin),
):
    tenant = tenant_service.actualizar_tenant(db, id_tenant, datos)
    bitacora_service.registrar(
        "TENANT_ACTUALIZADO",
        f"Admin actualizó el tenant '{tenant.NOMBRE}'",
        usuario=usuario,
        entidad="TENANT",
        id_entidad=tenant.ID_TENANT,
    )
    return tenant


@router.patch("/{id_tenant}/toggle-activo", response_model=TenantResponse)
def toggle_activo_tenant(
    id_tenant: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_admin),
):
    tenant = tenant_service.obtener_tenant_por_id(db, id_tenant)
    actualizado = tenant_service.actualizar_tenant(
        db,
        id_tenant,
        TenantUpdate(activo=not tenant.ACTIVO),
    )
    bitacora_service.registrar(
        "TENANT_ACTUALIZADO",
        f"Admin {'activó' if actualizado.ACTIVO else 'desactivó'} el tenant '{actualizado.NOMBRE}'",
        usuario=usuario,
        entidad="TENANT",
        id_entidad=actualizado.ID_TENANT,
    )
    return actualizado
