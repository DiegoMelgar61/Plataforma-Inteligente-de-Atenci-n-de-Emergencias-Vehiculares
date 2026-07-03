"""
Reportes personalizados (xlsx / pdf) por búsqueda. Solo TALLER (su tenant) y ADMIN.
"""
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.users.models import USUARIOS
from app.modules.reports import service as report_service
from app.modules.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/reports", tags=["Reportes"])

logger = logging.getLogger(__name__)

_XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _rol(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.get(
    "/incidents",
    summary="Reporte de incidentes (xlsx/pdf)",
    description=(
        "Descarga un reporte de incidentes filtrado. `formato=xlsx|pdf`. "
        "TALLER ve solo su tenant; ADMIN ve todo o filtra con `id_tenant`."
    ),
)
def reporte_incidentes(
    formato: str = Query("xlsx", pattern="^(xlsx|pdf)$"),
    estado: str | None = None,
    clasificacion: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    id_tenant: UUID | None = Query(None, description="Filtrar por tenant (solo ADMIN)"),
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    rol = _rol(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden generar reportes")

    if rol == "TALLER":
        tenant_efectivo = getattr(usuario, "_id_tenant", None) or usuario.ID_TENANT
    else:
        tenant_efectivo = id_tenant

    columnas, filas = report_service.construir_reporte_incidentes(
        db,
        tenant_efectivo=tenant_efectivo,
        estado=estado,
        clasificacion=clasificacion,
        desde=desde,
        hasta=hasta,
    )

    titulo = "Reporte de incidentes"
    stamp = datetime.now().strftime("%Y%m%d_%H%M")

    if formato == "xlsx":
        data = report_service.generar_xlsx(titulo, columnas, filas)
        media = _XLSX_MEDIA
        filename = f"reporte_incidentes_{stamp}.xlsx"
    else:
        data = report_service.generar_pdf(titulo, columnas, filas)
        media = "application/pdf"
        filename = f"reporte_incidentes_{stamp}.pdf"

    return Response(
        content=data,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
