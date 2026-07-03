from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.tenants.models import Tenant
from app.modules.tenants.schemas import TenantCreate, TenantUpdate

TENANT_DEFAULT_ID = UUID("e76212eb-e845-411d-b37f-e0ec986564d8")


def crear_tenant(db: Session, datos: TenantCreate) -> Tenant:
    existente = db.query(Tenant).filter(Tenant.NOMBRE == datos.nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un tenant con ese nombre")
    tenant = Tenant(
        NOMBRE=datos.nombre,
        DESCRIPCION=datos.descripcion,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def obtener_tenants(db: Session, solo_activos: bool = False) -> list[Tenant]:
    q = db.query(Tenant)
    if solo_activos:
        q = q.filter(Tenant.ACTIVO.is_(True))
    return q.order_by(Tenant.NOMBRE).all()


def obtener_tenant_por_id(db: Session, id_tenant: UUID) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.ID_TENANT == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return tenant


def actualizar_tenant(db: Session, id_tenant: UUID, datos: TenantUpdate) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.ID_TENANT == id_tenant).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    if datos.nombre is not None:
        tenant.NOMBRE = datos.nombre
    if datos.descripcion is not None:
        tenant.DESCRIPCION = datos.descripcion
    if datos.activo is not None:
        tenant.ACTIVO = datos.activo
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant
