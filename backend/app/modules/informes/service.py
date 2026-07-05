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

import base64
import logging
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import httpx
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


def generar_contenido_ia(
    db: Session, incidente: INCIDENTES
) -> tuple[dict[str, str], bool, str | None]:
    """
    Pide a la IA el texto de cada sección de contenido del informe y devuelve
    (contenido, generado_por_ia, error_ia). Nunca lanza: ante cualquier falla
    devuelve textos de respaldo con generado_por_ia=False y el detalle del
    error en error_ia para que quede registrado (no silencioso).
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
        return contenido, True, None
    except Exception as exc:
        logger.exception(
            "Falla al generar contenido IA del informe para incidente %s",
            incidente.ID_INCIDENTE,
        )
        error_ia = f"IA: {type(exc).__name__}: {exc}"
        return {clave: _TEXTO_RESPALDO for clave in claves}, False, error_ia


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
    Genera el informe de servicio del incidente UNA sola vez y lo persiste con
    su ciclo de vida en la tabla `informes_servicio` (fuente de verdad):

    - Si ya existe un registro para el incidente, lo devuelve sin regenerar
      nada (idempotente ante re-transiciones a ATENDIDO o reingresos).
    - Si no existe, crea la fila en estado GENERANDO y al terminar la pasa a
      LISTO (con el JSON de la IA y la referencia al PDF) o a FALLIDO (con el
      detalle del error registrado — el fallo deja de ser silencioso).

    Nunca lanza: cualquier falla queda en la tabla y devuelve la fila (o None
    si ni siquiera pudo crearse el registro), sin romper la transición.
    """
    try:
        # Idempotencia: un informe por incidente, nunca se regenera.
        informe = (
            db.query(INFORMES_SERVICIO)
            .filter(INFORMES_SERVICIO.ID_INCIDENTE == id_incidente)
            .first()
        )
        if informe is not None:
            logger.info(
                "Informe ya existente para incidente %s (estado=%s); no se regenera",
                id_incidente,
                informe.ESTADO,
            )
            return informe

        incidente = (
            db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
        )
        if incidente is None:
            logger.warning("Informe: incidente %s no encontrado", id_incidente)
            return None

        informe = INFORMES_SERVICIO(
            ID_INCIDENTE=id_incidente,
            ID_TENANT=incidente.ID_TENANT,
            ESTADO="GENERANDO",
        )
        db.add(informe)
        db.commit()
        db.refresh(informe)
    except Exception:
        logger.exception(
            "Error al registrar el informe de servicio para incidente %s",
            id_incidente,
        )
        try:
            db.rollback()
        except Exception:
            pass
        return None

    try:
        datos_fijos = _recolectar_datos_fijos(db, incidente)
        contenido_ia, generado_por_ia, error_ia = generar_contenido_ia(db, incidente)
        pdf_bytes = construir_pdf_informe(
            incidente=incidente,
            datos_fijos=datos_fijos,
            contenido_ia=contenido_ia,
        )

        destino_dir = Path(settings.UPLOADS_DIR) / "informes" / str(id_incidente)
        destino_dir.mkdir(parents=True, exist_ok=True)
        nombre_disco = f"informe_{uuid.uuid4().hex}.pdf"
        (destino_dir / nombre_disco).write_bytes(pdf_bytes)

        informe.ESTADO = "LISTO"
        informe.CONTENIDO_IA = contenido_ia
        informe.CLAVE_ARCHIVO = f"informes/{id_incidente}/{nombre_disco}"
        informe.URL_ARCHIVO = (
            f"{settings.INFORMES_URL_PREFIX}/{id_incidente}/{nombre_disco}"
        )
        informe.GENERADO_POR_IA = generado_por_ia
        # Si la IA falló pero el PDF salió con textos de respaldo, el informe
        # queda LISTO pero el error de IA queda registrado igual.
        informe.ERROR_DETALLE = error_ia
        informe.FECHA_GENERACION = datetime.now(timezone.utc)
        db.commit()
        db.refresh(informe)
        logger.info(
            "Informe de servicio generado para incidente %s (ia=%s)",
            id_incidente,
            generado_por_ia,
        )
        return informe
    except Exception as exc:
        logger.exception(
            "Error al generar/persistir informe de servicio para incidente %s",
            id_incidente,
        )
        try:
            db.rollback()
            informe.ESTADO = "FALLIDO"
            informe.ERROR_DETALLE = f"{type(exc).__name__}: {exc}"
            informe.FECHA_GENERACION = datetime.now(timezone.utc)
            db.commit()
            db.refresh(informe)
            return informe
        except Exception:
            logger.exception(
                "No se pudo registrar el fallo del informe para incidente %s",
                id_incidente,
            )
            try:
                db.rollback()
            except Exception:
                pass
            return None


# ─────────────────────────── Envío del informe por correo ────────────────────

_RESEND_API_URL = "https://api.resend.com/emails"


def _construir_html_correo(incidente: INCIDENTES, nombre_cliente: str) -> str:
    """Cuerpo simple del correo; el contenido real del servicio va en el PDF adjunto."""
    return f"""
    <div style="font-family: Arial, sans-serif; color: #111827;">
      <p>Hola {nombre_cliente or "cliente"},</p>
      <p>Adjuntamos el <b>informe de servicio</b> de tu orden
      #{incidente.ID_INCIDENTE:04d}, generado automáticamente al finalizar la atención.</p>
      <p>Gracias por confiar en {settings.APP_NAME}.</p>
    </div>
    """.strip()


def _registrar_error_correo(db: Session, informe: INFORMES_SERVICIO, detalle: str) -> None:
    """Deja el fallo del correo registrado en la tabla sin tocar el estado del
    informe (el PDF sigue LISTO y disponible en la orden)."""
    try:
        previo = f"{informe.ERROR_DETALLE} | " if informe.ERROR_DETALLE else ""
        informe.ERROR_DETALLE = f"{previo}Correo: {detalle}"
        db.commit()
    except Exception:
        logger.exception("No se pudo registrar el error de correo en la tabla")
        try:
            db.rollback()
        except Exception:
            pass


def enviar_correo_informe(db: Session, id_incidente: int) -> bool:
    """
    Envía por correo el PDF del informe de servicio YA generado y persistido
    (no lo vuelve a generar) al cliente del incidente, vía la API HTTP de Resend.

    Solo envía cuando el informe está LISTO y aún no fue enviado
    (CORREO_ENVIADO marca el envío y lo hace idempotente). Nunca lanza: ante
    cualquier falla registra el detalle en ERROR_DETALLE de la tabla —el fallo
    no es silencioso— y devuelve False, sin afectar la transición del incidente
    ni la disponibilidad del PDF en la orden.
    """
    informe = None
    try:
        informe = (
            db.query(INFORMES_SERVICIO)
            .filter(INFORMES_SERVICIO.ID_INCIDENTE == id_incidente)
            .first()
        )
        if informe is None:
            logger.warning(
                "No hay informe persistido para incidente %s; no se envía correo",
                id_incidente,
            )
            return False

        if _enum_a_texto(informe.ESTADO) != "LISTO" or not informe.CLAVE_ARCHIVO:
            logger.warning(
                "Informe del incidente %s no está LISTO (estado=%s); no se envía correo",
                id_incidente,
                informe.ESTADO,
            )
            return False

        if informe.CORREO_ENVIADO:
            logger.info(
                "Correo del informe ya enviado para incidente %s; no se reenvía",
                id_incidente,
            )
            return True

        if not settings.RESEND_API_KEY or not settings.RESEND_FROM_EMAIL:
            _registrar_error_correo(
                db, informe, "RESEND_API_KEY/RESEND_FROM_EMAIL no configurados"
            )
            return False

        incidente = (
            db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
        )
        if incidente is None:
            return False

        cliente = (
            db.query(USUARIOS)
            .filter(USUARIOS.ID_USUARIO == incidente.ID_USUARIO_CLIENTE)
            .first()
        )
        if cliente is None or not cliente.CORREO_ELECTRONICO:
            _registrar_error_correo(db, informe, "cliente sin correo electrónico")
            return False

        # Reutiliza el PDF ya persistido en disco; no se vuelve a generar.
        ruta_pdf = Path(settings.UPLOADS_DIR) / informe.CLAVE_ARCHIVO
        if not ruta_pdf.is_file():
            _registrar_error_correo(
                db, informe, f"archivo no encontrado en disco: {informe.CLAVE_ARCHIVO}"
            )
            return False

        pdf_base64 = base64.b64encode(ruta_pdf.read_bytes()).decode("ascii")
        nombre_archivo = f"informe_servicio_{id_incidente:04d}.pdf"

        payload = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [cliente.CORREO_ELECTRONICO],
            "subject": f"Informe de servicio - Orden #{incidente.ID_INCIDENTE:04d}",
            "html": _construir_html_correo(incidente, cliente.NOMBRE_COMPLETO),
            "attachments": [
                {"filename": nombre_archivo, "content": pdf_base64}
            ],
        }

        respuesta = httpx.post(
            _RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20.0,
        )
        respuesta.raise_for_status()

        informe.CORREO_ENVIADO = True
        db.commit()
        logger.info(
            "Informe de servicio enviado por correo para incidente %s a %s",
            id_incidente,
            cliente.CORREO_ELECTRONICO,
        )
        return True
    except Exception as exc:
        logger.exception(
            "Error al enviar por correo el informe de servicio del incidente %s",
            id_incidente,
        )
        try:
            db.rollback()
        except Exception:
            pass
        if informe is not None:
            _registrar_error_correo(db, informe, f"{type(exc).__name__}: {exc}")
        return False
