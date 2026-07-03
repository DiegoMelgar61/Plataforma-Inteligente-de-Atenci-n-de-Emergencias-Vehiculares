"""
Copias de respaldo de la base de datos. Solo ADMIN.
La descarga manual genera un .sql con el estado de los datos.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import USUARIOS
from app.modules.backups import service as backup_service
from app.modules.bitacora import service as bitacora_service
from app.modules.auth.dependencies import get_current_admin

router = APIRouter(prefix="/backups", tags=["Copias de respaldo"])

logger = logging.getLogger(__name__)


@router.get(
    "/manual",
    summary="Descargar respaldo SQL (Admin)",
    description="Genera y descarga un archivo .sql con el estado actual de los datos.",
)
def descargar_respaldo_manual(
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_admin),
):
    sql = backup_service.generar_dump_sql(db)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"backup_{stamp}.sql"

    bitacora_service.registrar(
        "BACKUP_DESCARGADO",
        f"Admin descargó respaldo SQL ({filename})",
        usuario=usuario,
        entidad="BACKUP",
    )

    return Response(
        content=sql,
        media_type="application/sql",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
