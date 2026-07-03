"""
KPIs y estadísticas del dashboard, filtrados por tenant.

Roles:
- TALLER: ve únicamente su propio tenant.
- ADMIN: ve todo por defecto; puede filtrar por ?id_tenant=<uuid>.
"""
import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    ASIGNACIONES,
    HISTORIAL_INCIDENTES,
    INCIDENTES,
    PAGOS,
    TALLERES,
)
from app.modules.users.models import USUARIOS
from app.modules.auth.dependencies import get_current_active_user
from app.presentation.api.v1.schemas.stats import (
    DashboardStatsResponse,
    IncidentesPorClasificacion,
    IncidentesPorDia,
    IncidentesPorEstado,
    TallerTop,
)

router = APIRouter(prefix="/stats", tags=["Estadísticas"])

logger = logging.getLogger(__name__)


def _rol(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    summary="KPIs del dashboard",
    description=(
        "Devuelve métricas clave calculadas en tiempo real desde la base de datos.\n\n"
        "- **TALLER**: ve solo su propio tenant.\n"
        "- **ADMIN**: ve todo o puede filtrar con `?id_tenant=<uuid>`."
    ),
)
def dashboard_stats(
    id_tenant: UUID | None = Query(
        None, description="Filtrar por tenant (solo ADMIN). TALLER siempre ve el suyo."
    ),
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    rol = _rol(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden ver estadísticas")

    # Resolver el tenant efectivo para el filtro
    if rol == "TALLER":
        tenant_efectivo = getattr(usuario, "_id_tenant", None) or usuario.ID_TENANT
    else:  # ADMIN
        tenant_efectivo = id_tenant  # None = sin filtro (ve todo)

    def _filtro_inc(q):
        if tenant_efectivo:
            return q.filter(INCIDENTES.ID_TENANT == tenant_efectivo)
        return q

    # ── 1. Total de incidentes ─────────────────────────────────────────────────
    total_incidentes: int = _filtro_inc(db.query(func.count(INCIDENTES.ID_INCIDENTE))).scalar() or 0

    # ── 2. Incidentes por estado ───────────────────────────────────────────────
    filas_estado = (
        _filtro_inc(
            db.query(INCIDENTES.ESTADO, func.count().label("total"))
        )
        .group_by(INCIDENTES.ESTADO)
        .all()
    )
    incidentes_por_estado = [
        IncidentesPorEstado(
            estado=r.ESTADO.value if hasattr(r.ESTADO, "value") else str(r.ESTADO),
            total=r.total,
        )
        for r in filas_estado
    ]

    # ── 3. Tiempo promedio de atención en minutos ──────────────────────────────
    # Usa historial_incidentes para encontrar cuándo cada incidente llegó a ATENDIDO
    sub_atendido = (
        db.query(
            HISTORIAL_INCIDENTES.ID_INCIDENTE.label("id_incidente"),
            func.min(HISTORIAL_INCIDENTES.FECHA_CAMBIO).label("primera_vez_atendido"),
        )
        .filter(HISTORIAL_INCIDENTES.ESTADO == "ATENDIDO")
        .group_by(HISTORIAL_INCIDENTES.ID_INCIDENTE)
        .subquery()
    )

    q_avg = db.query(
        func.avg(
            func.extract(
                "epoch",
                sub_atendido.c.primera_vez_atendido - INCIDENTES.FECHA_CREACION,
            )
            / 60
        )
    ).join(sub_atendido, INCIDENTES.ID_INCIDENTE == sub_atendido.c.id_incidente)
    if tenant_efectivo:
        q_avg = q_avg.filter(INCIDENTES.ID_TENANT == tenant_efectivo)
    tiempo_promedio_atencion: float | None = q_avg.scalar()
    if tiempo_promedio_atencion is not None:
        tiempo_promedio_atencion = round(float(tiempo_promedio_atencion), 1)

    # ── 4. Distribución por clasificación ─────────────────────────────────────
    filas_clas = (
        _filtro_inc(
            db.query(INCIDENTES.CLASIFICACION, func.count().label("total"))
        )
        .group_by(INCIDENTES.CLASIFICACION)
        .all()
    )
    incidentes_por_clasificacion = [
        IncidentesPorClasificacion(
            clasificacion=(
                r.CLASIFICACION.value if hasattr(r.CLASIFICACION, "value")
                else str(r.CLASIFICACION)
            ),
            total=r.total,
        )
        for r in filas_clas
    ]

    # ── 5. Total recaudado en pagos confirmados ────────────────────────────────
    q_recaudado = (
        db.query(func.sum(PAGOS.MONTO))
        .join(INCIDENTES, PAGOS.ID_INCIDENTE == INCIDENTES.ID_INCIDENTE)
        .filter(PAGOS.ESTADO == "PAGADO")
    )
    if tenant_efectivo:
        q_recaudado = q_recaudado.filter(INCIDENTES.ID_TENANT == tenant_efectivo)
    total_recaudado: float = float(q_recaudado.scalar() or 0)

    # ── 6. Taller con más incidentes atendidos ────────────────────────────────
    q_top = (
        db.query(
            TALLERES.ID_TALLER,
            TALLERES.NOMBRE_NEGOCIO,
            func.count().label("total_atendidos"),
        )
        .join(ASIGNACIONES, TALLERES.ID_TALLER == ASIGNACIONES.ID_TALLER)
        .join(INCIDENTES, ASIGNACIONES.ID_INCIDENTE == INCIDENTES.ID_INCIDENTE)
        .filter(INCIDENTES.ESTADO == "ATENDIDO")
    )
    if tenant_efectivo:
        q_top = q_top.filter(INCIDENTES.ID_TENANT == tenant_efectivo)
    fila_top = (
        q_top.group_by(TALLERES.ID_TALLER, TALLERES.NOMBRE_NEGOCIO)
        .order_by(desc("total_atendidos"))
        .first()
    )
    taller_top = (
        TallerTop(
            id_taller=fila_top.ID_TALLER,
            nombre_negocio=fila_top.NOMBRE_NEGOCIO,
            total_atendidos=fila_top.total_atendidos,
        )
        if fila_top
        else None
    )

    # ── 7. Incidentes por día — últimos 7 días ────────────────────────────────
    hace_7_dias = datetime.utcnow() - timedelta(days=7)
    q_dias = (
        db.query(
            func.date(INCIDENTES.FECHA_CREACION).label("dia"),
            func.count().label("total"),
        )
        .filter(INCIDENTES.FECHA_CREACION >= hace_7_dias)
    )
    if tenant_efectivo:
        q_dias = q_dias.filter(INCIDENTES.ID_TENANT == tenant_efectivo)
    filas_dias = (
        q_dias.group_by(func.date(INCIDENTES.FECHA_CREACION))
        .order_by(func.date(INCIDENTES.FECHA_CREACION))
        .all()
    )
    incidentes_ultimos_7_dias = [
        IncidentesPorDia(dia=str(r.dia), total=r.total) for r in filas_dias
    ]

    # ── 8. Porcentaje de incidentes atendidos vs total ─────────────────────────
    total_base = total_incidentes or 1  # evitar división por cero
    atendidos = next(
        (r.total for r in incidentes_por_estado if r.estado == "ATENDIDO"), 0
    )
    porcentaje_atendidos = round((atendidos / total_base) * 100, 1)

    return DashboardStatsResponse(
        total_incidentes=total_incidentes,
        incidentes_por_estado=incidentes_por_estado,
        tiempo_promedio_atencion_minutos=tiempo_promedio_atencion,
        incidentes_por_clasificacion=incidentes_por_clasificacion,
        total_recaudado=total_recaudado,
        taller_top=taller_top,
        incidentes_ultimos_7_dias=incidentes_ultimos_7_dias,
        porcentaje_atendidos=porcentaje_atendidos,
        filtrado_por_tenant=str(tenant_efectivo) if tenant_efectivo else None,
    )


@router.get(
    "/zonas",
    summary="Zonas con más incidentes (mapa de calor)",
    description="Agrupa los incidentes por celda geográfica para pintar manchas en el mapa.",
)
def zonas_incidentes(
    id_tenant: UUID | None = Query(None, description="Filtrar por tenant (solo ADMIN)"),
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    rol = _rol(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden ver el mapa de calor")

    if rol == "TALLER":
        tenant_efectivo = getattr(usuario, "_id_tenant", None) or usuario.ID_TENANT
    else:
        tenant_efectivo = id_tenant

    sql = (
        "SELECT ST_Y(ubicacion::geometry) AS lat, ST_X(ubicacion::geometry) AS lon "
        "FROM incidentes WHERE ubicacion IS NOT NULL"
    )
    params: dict = {}
    if tenant_efectivo:
        sql += " AND id_tenant = :t"
        params["t"] = str(tenant_efectivo)

    filas = db.execute(text(sql), params).fetchall()

    # Agrupar por celda (~400m) para formar manchas.
    celda = 0.004
    grilla: dict[tuple, list] = {}
    for lat, lon in filas:
        if lat is None or lon is None:
            continue
        clave = (round(lat / celda), round(lon / celda))
        g = grilla.setdefault(clave, [0, 0.0, 0.0])
        g[0] += 1
        g[1] += lat
        g[2] += lon

    total = sum(g[0] for g in grilla.values()) or 1
    zonas = [
        {
            "lat": g[1] / g[0],
            "lon": g[2] / g[0],
            "total": g[0],
            "porcentaje": round(g[0] * 100 / total, 1),
        }
        for g in grilla.values()
    ]
    zonas.sort(key=lambda z: z["total"], reverse=True)
    return zonas
