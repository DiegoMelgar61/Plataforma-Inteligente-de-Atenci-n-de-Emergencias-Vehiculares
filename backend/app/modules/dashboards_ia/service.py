"""
Dashboards IA: a partir de un pedido en texto o audio, la IA (Gemini) decide
QUÉ métricas y QUÉ tipo de gráfico mostrar (de un catálogo cerrado), y el
backend calcula los DATOS REALES desde la base (tenant-scoped). La IA nunca
inventa números: solo elige métrica + tipo de gráfico + período.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.incidents.models import INCIDENTES
from app.modules.assignments.models import ASIGNACIONES
from app.modules.payments.models import PAGOS
from app.modules.technicians.models import TECNICOS
from app.modules.workshops.models import TALLERES

logger = logging.getLogger(__name__)

TIPOS_GRAFICO = {"bar", "line", "pie", "doughnut"}


# ── Resolución de períodos ────────────────────────────────────────────────────

def _rango(periodo: str | None) -> tuple[datetime | None, datetime | None]:
    ahora = datetime.now()
    if periodo == "hoy":
        return ahora.replace(hour=0, minute=0, second=0, microsecond=0), None
    if periodo == "semana":
        return ahora - timedelta(days=7), None
    if periodo == "mes_actual":
        return ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0), None
    return None, None  # "todo"


def _aplicar_filtros(q, desde, hasta):
    if desde:
        q = q.filter(INCIDENTES.FECHA_CREACION >= desde)
    if hasta:
        q = q.filter(INCIDENTES.FECHA_CREACION <= hasta)
    return q


def _val(v) -> str:
    return v.value if hasattr(v, "value") else str(v)


# ── Cálculo de cada métrica (tenant-scoped) ──────────────────────────────────

def _m_desempeno_por_taller(db, tenant, desde, hasta) -> dict:
    q = (
        db.query(TALLERES.NOMBRE_NEGOCIO, func.count(INCIDENTES.ID_INCIDENTE))
        .join(ASIGNACIONES, ASIGNACIONES.ID_TALLER == TALLERES.ID_TALLER)
        .join(INCIDENTES, INCIDENTES.ID_INCIDENTE == ASIGNACIONES.ID_INCIDENTE)
        .filter(INCIDENTES.ESTADO == "ATENDIDO")
    )
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(TALLERES.NOMBRE_NEGOCIO).order_by(func.count(INCIDENTES.ID_INCIDENTE).desc())
    filas = q.all()
    return {"labels": [r[0] for r in filas], "series": [{"label": "Atendidos", "data": [r[1] for r in filas]}]}


def _m_tecnico_top(db, tenant, desde, hasta) -> dict:
    q = (
        db.query(TECNICOS.NOMBRE_COMPLETO, func.count(INCIDENTES.ID_INCIDENTE))
        .join(ASIGNACIONES, ASIGNACIONES.ID_TECNICO == TECNICOS.ID_TECNICO)
        .join(INCIDENTES, INCIDENTES.ID_INCIDENTE == ASIGNACIONES.ID_INCIDENTE)
    )
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(TECNICOS.NOMBRE_COMPLETO).order_by(func.count(INCIDENTES.ID_INCIDENTE).desc()).limit(10)
    filas = q.all()
    return {"labels": [r[0] for r in filas], "series": [{"label": "Llamados atendidos", "data": [r[1] for r in filas]}]}


def _m_clasificacion_recurrente(db, tenant, desde, hasta) -> dict:
    q = db.query(INCIDENTES.CLASIFICACION, func.count(INCIDENTES.ID_INCIDENTE))
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(INCIDENTES.CLASIFICACION).order_by(func.count(INCIDENTES.ID_INCIDENTE).desc())
    filas = q.all()
    return {"labels": [_val(r[0]) for r in filas], "series": [{"label": "Incidentes", "data": [r[1] for r in filas]}]}


def _m_incidentes_por_estado(db, tenant, desde, hasta) -> dict:
    q = db.query(INCIDENTES.ESTADO, func.count(INCIDENTES.ID_INCIDENTE))
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(INCIDENTES.ESTADO)
    filas = q.all()
    return {"labels": [_val(r[0]) for r in filas], "series": [{"label": "Incidentes", "data": [r[1] for r in filas]}]}


def _m_incidentes_por_prioridad(db, tenant, desde, hasta) -> dict:
    q = db.query(INCIDENTES.PRIORIDAD, func.count(INCIDENTES.ID_INCIDENTE))
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(INCIDENTES.PRIORIDAD)
    filas = q.all()
    return {"labels": [_val(r[0]) for r in filas], "series": [{"label": "Incidentes", "data": [r[1] for r in filas]}]}


def _m_incidentes_por_dia(db, tenant, desde, hasta) -> dict:
    dia = func.date(INCIDENTES.FECHA_CREACION)
    q = db.query(dia.label("dia"), func.count(INCIDENTES.ID_INCIDENTE))
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(dia).order_by(dia)
    filas = q.all()
    return {"labels": [str(r[0]) for r in filas], "series": [{"label": "Incidentes por día", "data": [r[1] for r in filas]}]}


def _m_ingresos_por_taller(db, tenant, desde, hasta) -> dict:
    q = (
        db.query(TALLERES.NOMBRE_NEGOCIO, func.coalesce(func.sum(PAGOS.MONTO), 0))
        .join(PAGOS, PAGOS.ID_TALLER == TALLERES.ID_TALLER)
        .join(INCIDENTES, INCIDENTES.ID_INCIDENTE == PAGOS.ID_INCIDENTE)
        .filter(PAGOS.ESTADO == "PAGADO")
    )
    if tenant:
        q = q.filter(INCIDENTES.ID_TENANT == tenant)
    q = _aplicar_filtros(q, desde, hasta).group_by(TALLERES.NOMBRE_NEGOCIO).order_by(func.sum(PAGOS.MONTO).desc())
    filas = q.all()
    return {"labels": [r[0] for r in filas], "series": [{"label": "Ingresos (Bs.)", "data": [float(r[1]) for r in filas]}]}


# ── Catálogo: clave → (descripción para la IA, tipo sugerido, función) ────────

CATALOGO: dict[str, dict] = {
    "desempeno_por_taller": {"desc": "Cantidad de incidentes atendidos por cada taller", "tipo": "bar", "fn": _m_desempeno_por_taller},
    "tecnico_top": {"desc": "Técnicos que más llamados atendieron (ranking)", "tipo": "bar", "fn": _m_tecnico_top},
    "clasificacion_recurrente": {"desc": "Tipos de problema más recurrentes (batería, llanta, motor, choque, etc.)", "tipo": "pie", "fn": _m_clasificacion_recurrente},
    "incidentes_por_estado": {"desc": "Distribución de incidentes por estado", "tipo": "doughnut", "fn": _m_incidentes_por_estado},
    "incidentes_por_prioridad": {"desc": "Distribución de incidentes por prioridad", "tipo": "pie", "fn": _m_incidentes_por_prioridad},
    "incidentes_por_dia": {"desc": "Tendencia de incidentes por día (línea temporal)", "tipo": "line", "fn": _m_incidentes_por_dia},
    "ingresos_por_taller": {"desc": "Ingresos cobrados (pagos confirmados) por taller", "tipo": "bar", "fn": _m_ingresos_por_taller},
}


# ── Interpretación del pedido (Gemini con fallback por reglas) ────────────────

def _prompt_interpretacion(texto: str | None) -> str:
    catalogo = "\n".join(f'- {k}: {v["desc"]}' for k, v in CATALOGO.items())
    pedido = (texto or "").strip() or "(el pedido viene en el audio adjunto, transcribilo)"
    return f"""Sos un asistente que arma dashboards. El usuario pide reportes en lenguaje natural.
Según el pedido, elegí qué paneles mostrar usando SOLO estas métricas disponibles:
{catalogo}

Tipos de gráfico válidos: bar, line, pie, doughnut.
Períodos válidos: hoy, semana, mes_actual, todo.

Respondé ÚNICAMENTE con un JSON válido, sin texto adicional, con esta forma:
{{
  "titulo": "título corto del informe",
  "orden": "el pedido del usuario en una frase (si vino en audio, transcribilo)",
  "paneles": [
    {{"titulo": "título del panel", "metrica": "<una clave del catálogo>", "tipo": "bar|line|pie|doughnut", "periodo": "hoy|semana|mes_actual|todo"}}
  ]
}}

Reglas:
- Usá solo claves de métrica que existan en el catálogo.
- Elegí el tipo de gráfico más adecuado para cada métrica.
- Incluí entre 1 y 4 paneles según lo que pida el usuario.

Pedido del usuario: {pedido}
"""


def _interpretar_por_reglas(texto: str | None) -> dict:
    """Fallback sin IA: elige métricas por palabras clave."""
    t = (texto or "").lower()
    paneles = []

    def add(metrica):
        if metrica in CATALOGO and not any(p["metrica"] == metrica for p in paneles):
            paneles.append({"titulo": CATALOGO[metrica]["desc"], "metrica": metrica, "tipo": CATALOGO[metrica]["tipo"], "periodo": periodo})

    periodo = "todo"
    if "mes" in t:
        periodo = "mes_actual"
    elif "semana" in t:
        periodo = "semana"
    elif "hoy" in t:
        periodo = "hoy"

    if "taller" in t or "desempeñ" in t or "desempen" in t:
        add("desempeno_por_taller")
    if "tecnic" in t or "técnic" in t:
        add("tecnico_top")
    if "recurrente" in t or "tipo" in t or "clasific" in t or "motor" in t or "llanta" in t:
        add("clasificacion_recurrente")
    if "estado" in t:
        add("incidentes_por_estado")
    if "prioridad" in t:
        add("incidentes_por_prioridad")
    if "día" in t or "dia" in t or "tendencia" in t or "evolución" in t or "evolucion" in t:
        add("incidentes_por_dia")
    if "ingreso" in t or "recaud" in t or "pago" in t or "dinero" in t:
        add("ingresos_por_taller")

    if not paneles:
        add("desempeno_por_taller")
        add("clasificacion_recurrente")

    return {"titulo": "Informe de desempeño", "orden": texto or "", "paneles": paneles[:4]}


def _interpretar(texto: str | None, audio_part: dict | None) -> dict:
    """Devuelve el spec {titulo, orden, paneles}. Usa Gemini; si falla, reglas."""
    if settings.GEMINI_API_KEY:
        try:
            from app.infrastructure.external_services.ai_service import _run_gemini
            spec = _run_gemini(prompt=_prompt_interpretacion(texto), audio_part=audio_part, image_part=None)
            if isinstance(spec, dict) and spec.get("paneles"):
                spec["_origen"] = "gemini"
                return spec
        except Exception:
            logger.exception("Interpretación Gemini falló; usando reglas")
    spec = _interpretar_por_reglas(texto)
    spec["_origen"] = "reglas"
    return spec


# ── Orquestación: generar el dashboard con datos reales ──────────────────────

def generar_dashboard(
    db: Session,
    *,
    tenant,
    texto: str | None = None,
    audio_part: dict | None = None,
) -> dict:
    spec = _interpretar(texto, audio_part)

    paneles_salida = []
    for panel in spec.get("paneles", [])[:4]:
        metrica = panel.get("metrica")
        entrada = CATALOGO.get(metrica)
        if not entrada:
            continue  # ignorar métricas inexistentes (la IA no puede inventar)
        tipo = panel.get("tipo") if panel.get("tipo") in TIPOS_GRAFICO else entrada["tipo"]
        desde, hasta = _rango(panel.get("periodo"))
        try:
            datos = entrada["fn"](db, tenant, desde, hasta)
        except Exception:
            logger.exception("Error calculando métrica %s", metrica)
            continue
        paneles_salida.append({
            "titulo": panel.get("titulo") or entrada["desc"],
            "metrica": metrica,
            "tipo": tipo,
            "periodo": panel.get("periodo") or "todo",
            "labels": datos["labels"],
            "series": datos["series"],
        })

    return {
        "titulo": spec.get("titulo") or "Informe IA",
        "orden": spec.get("orden") or (texto or ""),
        "origen": spec.get("_origen", "reglas"),
        "paneles": paneles_salida,
    }
