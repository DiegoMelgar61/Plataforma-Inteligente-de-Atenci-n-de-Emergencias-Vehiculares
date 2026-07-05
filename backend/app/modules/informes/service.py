"""
Generación del informe de servicio en PDF con IA al finalizar un incidente.

Diseño (reglas del feature):
- El armazón del PDF lo controla el CÓDIGO (encabezado, pie, tipografía y orden
  de secciones idénticos en todos los informes). La IA solo rellena el texto de
  cada sección de contenido.
- Se reutiliza el servicio de IA existente (`run_gemini`) y el armado de contexto
  del incidente del módulo de chat (`construir_contexto_incidente`), que ya es
  seguro por tenant (solo lee filas de ESTE incidente, nunca cruza tenants).
- Ante cualquier falla de la IA o de la generación del PDF, la función nunca
  propaga la excepción: registra el error y devuelve None, de modo que jamás
  rompe la transición del incidente a ATENDIDO.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.assignments.models import ASIGNACIONES
from app.modules.incidents.models import INCIDENTES
from app.modules.informes.models import INFORMES_SERVICIO
from app.modules.technicians.models import TECNICOS
from app.modules.tenants.models import Tenant
from app.modules.users.models import USUARIOS
from app.modules.vehicles.models import VEHICULOS
from app.modules.workshops.models import TALLERES

logger = logging.getLogger(__name__)

# Orden fijo de las secciones de contenido que aporta la IA: (clave_json, título).
# El código controla el orden; la IA solo rellena el texto de cada clave.
_SECCIONES_IA: list[tuple[str, str]] = [
    ("resumen_incidente", "Resumen del incidente"),
    ("diagnostico", "Diagnóstico"),
    ("trabajo_realizado", "Trabajo realizado"),
    ("estado_final", "Estado final"),
    ("recomendaciones_preventivas", "Recomendaciones preventivas"),
    ("proximos_pasos", "Próximos pasos sugeridos"),
]

_TEXTO_RESPALDO = "No disponible automáticamente. Requiere revisión manual."


def _enum_a_texto(valor) -> str:
    return valor.value if hasattr(valor, "value") else ("" if valor is None else str(valor))


def _ubicacion_texto(db: Session, incidente: INCIDENTES) -> str:
    """Extrae 'lat, lon' de la columna Geography de forma defensiva."""
    try:
        from geoalchemy2.functions import ST_X, ST_Y

        fila = (
            db.query(ST_Y(INCIDENTES.UBICACION), ST_X(INCIDENTES.UBICACION))
            .filter(INCIDENTES.ID_INCIDENTE == incidente.ID_INCIDENTE)
            .first()
        )
        if fila and fila[0] is not None and fila[1] is not None:
            return f"{float(fila[0]):.5f}, {float(fila[1]):.5f}"
    except Exception:  # pragma: no cover - PostGIS no disponible (p.ej. SQLite)
        pass
    return "—"


def _recolectar_datos_fijos(db: Session, incidente: INCIDENTES) -> dict[str, str]:
    """Datos de la sección fija del informe, tomados de la base (no de la IA)."""
    cliente = (
        db.query(USUARIOS)
        .filter(USUARIOS.ID_USUARIO == incidente.ID_USUARIO_CLIENTE)
        .first()
    )

    vehiculo_texto = "—"
    if incidente.ID_VEHICULO:
        vehiculo = (
            db.query(VEHICULOS)
            .filter(VEHICULOS.ID_VEHICULO == incidente.ID_VEHICULO)
            .first()
        )
        if vehiculo is not None:
            partes = [
                p
                for p in [
                    vehiculo.MARCA,
                    vehiculo.MODELO,
                    str(vehiculo.ANIO) if vehiculo.ANIO else None,
                ]
                if p
            ]
            base = " ".join(partes) if partes else "Vehículo registrado"
            vehiculo_texto = f"{base} ({vehiculo.PLACA})" if vehiculo.PLACA else base

    taller_texto = "—"
    tecnico_texto = "—"
    asignacion = (
        db.query(ASIGNACIONES)
        .filter(
            ASIGNACIONES.ID_INCIDENTE == incidente.ID_INCIDENTE,
            ASIGNACIONES.FECHA_RECHAZO.is_(None),
        )
        .first()
    )
    if asignacion is not None:
        taller = (
            db.query(TALLERES).filter(TALLERES.ID_TALLER == asignacion.ID_TALLER).first()
        )
        if taller is not None:
            taller_texto = taller.NOMBRE_NEGOCIO
        tecnico = (
            db.query(TECNICOS)
            .filter(TECNICOS.ID_TECNICO == asignacion.ID_TECNICO)
            .first()
        )
        if tecnico is not None:
            tecnico_texto = tecnico.NOMBRE_COMPLETO

    tenant_texto = "—"
    if incidente.ID_TENANT:
        tenant = (
            db.query(Tenant).filter(Tenant.ID_TENANT == incidente.ID_TENANT).first()
        )
        if tenant is not None:
            tenant_texto = tenant.NOMBRE

    return {
        "cliente": cliente.NOMBRE_COMPLETO if cliente else "—",
        "telefono_cliente": (cliente.TELEFONO if cliente and cliente.TELEFONO else "—"),
        "vehiculo": vehiculo_texto,
        "taller": taller_texto,
        "tecnico": tecnico_texto,
        "ubicacion": _ubicacion_texto(db, incidente),
        "clasificacion": _enum_a_texto(incidente.CLASIFICACION) or "—",
        "prioridad": _enum_a_texto(incidente.PRIORIDAD) or "—",
        "tenant": tenant_texto,
    }


def generar_contenido_ia(db: Session, incidente: INCIDENTES) -> tuple[dict[str, str], bool]:
    """
    Pide a la IA el texto de cada sección de contenido del informe y devuelve
    (contenido, generado_por_ia). Nunca lanza: ante cualquier falla devuelve
    textos de respaldo con generado_por_ia=False.
    """
    claves = [clave for clave, _ in _SECCIONES_IA]
    try:
        from app.infrastructure.external_services.ai_service import run_gemini
        from app.modules.chat.service import construir_contexto_incidente

        # Contexto completo del incidente incluyendo los chats de atención.
        # Solo abarca filas de ESTE incidente => aislamiento por tenant garantizado.
        contexto = construir_contexto_incidente(
            db, incidente, incluir_chat_cliente=True
        )

        estructura = ",\n".join(f'  "{clave}": "string"' for clave in claves)
        prompt = f"""Sos un mecánico especialista que redacta el informe final de un
servicio de asistencia vehicular ya atendido. A partir del contexto del incidente,
redactá el contenido de cada sección en español, claro y profesional.

Reglas:
- NUNCA inventes datos que no estén en el contexto. Si algo no consta, indicá que
  no hay información suficiente.
- No incluyas encabezados ni viñetas de markdown; solo el texto de cada sección.
- "proximos_pasos": sugerí acciones concretas (por ejemplo visita al taller para un
  arreglo de fondo, mantenimiento o revisión) según corresponda al caso.
- Respondé ÚNICAMENTE con un objeto JSON válido, sin texto adicional, con esta forma:
{{
{estructura}
}}

Contexto del incidente:
{contexto}
"""

        resultado = run_gemini(prompt=prompt)
        if not isinstance(resultado, dict):
            raise ValueError("La IA no devolvió un objeto JSON")

        contenido: dict[str, str] = {}
        for clave in claves:
            valor = resultado.get(clave)
            texto = valor.strip() if isinstance(valor, str) else ""
            contenido[clave] = texto or _TEXTO_RESPALDO
        return contenido, True
    except Exception:
        logger.exception(
            "Falla al generar contenido IA del informe para incidente %s",
            incidente.ID_INCIDENTE,
        )
        return {clave: _TEXTO_RESPALDO for clave in claves}, False


# ─────────────────────────── Construcción del PDF ────────────────────────────


def _dibujar_marco(canvas, doc) -> None:
    """Encabezado y pie fijos, idénticos en todas las páginas (control del código)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4

    ancho, alto = A4
    canvas.saveState()

    # Encabezado: nombre de la plataforma + rótulo, con línea divisoria.
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(colors.HexColor("#4F46E5"))
    canvas.drawString(24, alto - 34, settings.APP_NAME)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawRightString(ancho - 24, alto - 34, "Informe de Servicio")
    canvas.setStrokeColor(colors.HexColor("#D1D5DB"))
    canvas.line(24, alto - 40, ancho - 24, alto - 40)

    # Pie: aviso de generación automática + timestamp + número de página.
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    canvas.setStrokeColor(colors.HexColor("#D1D5DB"))
    canvas.line(24, 40, ancho - 24, 40)
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.setFillColor(colors.HexColor("#9CA3AF"))
    canvas.drawString(
        24, 30, f"Informe generado automáticamente por IA · {ts}"
    )
    canvas.drawRightString(ancho - 24, 30, f"Página {doc.page}")
    canvas.restoreState()


def construir_pdf_informe(
    *,
    incidente: INCIDENTES,
    datos_fijos: dict[str, str],
    contenido_ia: dict[str, str],
) -> bytes:
    """Arma el PDF con plantilla fija en código, inyectando datos y texto IA."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=56,
        bottomMargin=52,
        title=f"Informe de Servicio - Orden #{incidente.ID_INCIDENTE:04d}",
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloInforme",
        parent=estilos["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor=colors.HexColor("#111827"),
    )
    subtitulo = ParagraphStyle(
        "SubInforme",
        parent=estilos["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#6B7280"),
    )
    encabezado_seccion = ParagraphStyle(
        "EncabezadoSeccion",
        parent=estilos["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor("#4F46E5"),
    )
    cuerpo = ParagraphStyle(
        "CuerpoInforme",
        parent=estilos["BodyText"],
        fontSize=10,
        leading=14,
    )

    fecha = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    elementos: list = [
        Paragraph("Informe de Servicio", titulo),
        Paragraph(
            f"Orden #{incidente.ID_INCIDENTE:04d} · Fecha: {fecha} · "
            f"Tenant: {datos_fijos['tenant']}",
            subtitulo,
        ),
        Spacer(1, 12),
    ]

    # Sección fija: datos del servicio, desde la base de datos.
    filas_datos = [
        ["Cliente", datos_fijos["cliente"]],
        ["Teléfono", datos_fijos["telefono_cliente"]],
        ["Vehículo", datos_fijos["vehiculo"]],
        ["Taller", datos_fijos["taller"]],
        ["Técnico", datos_fijos["tecnico"]],
        ["Ubicación", datos_fijos["ubicacion"]],
        ["Clasificación", datos_fijos["clasificacion"]],
        ["Prioridad", datos_fijos["prioridad"]],
    ]
    tabla = Table(
        [[Paragraph(f"<b>{k}</b>", cuerpo), Paragraph(str(v), cuerpo)] for k, v in filas_datos],
        colWidths=[110, doc.width - 110],
    )
    tabla.setStyle(
        TableStyle(
            [
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabla)

    # Secciones de contenido IA, en orden fijo controlado por el código.
    for clave, titulo_seccion in _SECCIONES_IA:
        texto = (contenido_ia.get(clave) or "").strip() or _TEXTO_RESPALDO
        elementos.append(Paragraph(titulo_seccion, encabezado_seccion))
        elementos.append(Paragraph(texto.replace("\n", "<br/>"), cuerpo))

    doc.build(elementos, onFirstPage=_dibujar_marco, onLaterPages=_dibujar_marco)
    return buf.getvalue()


# ─────────────────────────── Orquestación / persistencia ─────────────────────


def generar_y_persistir_informe(db: Session, id_incidente: int) -> INFORMES_SERVICIO | None:
    """
    Genera el informe de servicio del incidente y lo persiste (archivo en disco
    + fila de metadatos). Nunca lanza: ante cualquier falla registra y devuelve
    None para no romper la transición a ATENDIDO.
    """
    try:
        incidente = (
            db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
        )
        if incidente is None:
            logger.warning("Informe: incidente %s no encontrado", id_incidente)
            return None

        datos_fijos = _recolectar_datos_fijos(db, incidente)
        contenido_ia, generado_por_ia = generar_contenido_ia(db, incidente)
        pdf_bytes = construir_pdf_informe(
            incidente=incidente,
            datos_fijos=datos_fijos,
            contenido_ia=contenido_ia,
        )

        destino_dir = Path(settings.UPLOADS_DIR) / "informes" / str(id_incidente)
        destino_dir.mkdir(parents=True, exist_ok=True)
        nombre_disco = f"informe_{uuid.uuid4().hex}.pdf"
        (destino_dir / nombre_disco).write_bytes(pdf_bytes)

        clave = f"informes/{id_incidente}/{nombre_disco}"
        url = f"{settings.INFORMES_URL_PREFIX}/{id_incidente}/{nombre_disco}"

        informe = (
            db.query(INFORMES_SERVICIO)
            .filter(INFORMES_SERVICIO.ID_INCIDENTE == id_incidente)
            .first()
        )
        if informe is None:
            informe = INFORMES_SERVICIO(ID_INCIDENTE=id_incidente)
            db.add(informe)
        informe.URL_ARCHIVO = url
        informe.CLAVE_ARCHIVO = clave
        informe.GENERADO_POR_IA = generado_por_ia
        informe.ID_TENANT = incidente.ID_TENANT

        db.commit()
        db.refresh(informe)
        logger.info(
            "Informe de servicio generado para incidente %s (ia=%s)",
            id_incidente,
            generado_por_ia,
        )
        return informe
    except Exception:
        logger.exception(
            "Error al generar/persistir informe de servicio para incidente %s",
            id_incidente,
        )
        try:
            db.rollback()
        except Exception:
            pass
        return None
