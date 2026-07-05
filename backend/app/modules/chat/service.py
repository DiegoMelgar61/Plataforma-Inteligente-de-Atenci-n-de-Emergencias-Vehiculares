"""
Lógica de dominio del chat de IA por incidente.

Dos hilos conectados:
- CLIENTE: la IA actúa como mecánico especialista en emergencias vehiculares,
  da instrucciones de seguridad y recolecta detalles nuevos mientras el
  técnico está en camino.
- TECNICO: copiloto de taller que sugiere herramientas y repuestos probables
  según el tipo de incidente y todo lo conversado en el hilo del cliente
  (puente de contexto cliente -> técnico).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.infrastructure.external_services.ai_service import run_gemini
from app.modules.chat.models import CONVERSACIONES, MENSAJES_CHAT
from app.modules.incidents.models import EVIDENCIAS, INCIDENTES
from app.modules.vehicles.models import VEHICULOS

logger = logging.getLogger(__name__)

_FALLBACK_CLIENTE = (
    "En este momento no puedo procesar tu mensaje. Si estás en una situación de "
    "riesgo, mantente en un lugar seguro alejado del tráfico y espera al técnico "
    "asignado."
)

_FALLBACK_TECNICO = (
    "No fue posible generar una sugerencia en este momento. Revisá la "
    "clasificación del incidente y el chat del cliente para preparar herramientas "
    "y repuestos básicos según el tipo de falla reportado."
)

_MAX_HISTORIAL_MENSAJES = 20


def _enum_a_texto(valor) -> str:
    return valor.value if hasattr(valor, "value") else str(valor)


def obtener_o_crear_conversacion(
    db: Session, incidente: INCIDENTES, tipo: str
) -> tuple[CONVERSACIONES, bool]:
    """Get-or-create idempotente. Devuelve (conversacion, fue_creada)."""
    conversacion = (
        db.query(CONVERSACIONES)
        .filter(
            CONVERSACIONES.ID_INCIDENTE == incidente.ID_INCIDENTE,
            CONVERSACIONES.TIPO == tipo,
        )
        .first()
    )
    if conversacion is not None:
        return conversacion, False

    conversacion = CONVERSACIONES(
        ID_INCIDENTE=incidente.ID_INCIDENTE,
        TIPO=tipo,
        ID_TENANT=incidente.ID_TENANT,
    )
    db.add(conversacion)
    db.flush()
    return conversacion, True


def construir_contexto_incidente(
    db: Session, incidente: INCIDENTES, *, incluir_chat_cliente: bool = False
) -> str:
    """
    Arma un bloque de contexto compacto en español con los datos del incidente:
    estado, clasificación, prioridad, resumen IA, vehículo y evidencias.
    Todo restringido a las filas de ESTE incidente (nunca cruza tenants).
    """
    lineas: list[str] = []

    lineas.append(f"Estado actual: {_enum_a_texto(incidente.ESTADO)}")
    lineas.append(f"Clasificación: {_enum_a_texto(incidente.CLASIFICACION)}")
    lineas.append(f"Prioridad: {_enum_a_texto(incidente.PRIORIDAD)}")
    if incidente.RESUMEN_IA:
        lineas.append(f"Resumen IA: {incidente.RESUMEN_IA}")

    if incidente.ID_VEHICULO:
        vehiculo = (
            db.query(VEHICULOS)
            .filter(VEHICULOS.ID_VEHICULO == incidente.ID_VEHICULO)
            .first()
        )
        if vehiculo is not None:
            datos_vehiculo = " ".join(
                filter(
                    None,
                    [
                        vehiculo.MARCA,
                        vehiculo.MODELO,
                        str(vehiculo.ANIO) if vehiculo.ANIO else None,
                    ],
                )
            )
            if datos_vehiculo:
                lineas.append(f"Vehículo: {datos_vehiculo}")

    evidencias = (
        db.query(EVIDENCIAS)
        .filter(EVIDENCIAS.ID_INCIDENTE == incidente.ID_INCIDENTE)
        .order_by(EVIDENCIAS.FECHA_CREACION)
        .all()
    )
    resumenes_evidencia: list[str] = []
    for ev in evidencias:
        if ev.TEXTO_TRANSCRITO:
            resumenes_evidencia.append(f"- {ev.TEXTO_TRANSCRITO.strip()}")
        if ev.ANALISIS_IA:
            resumenes_evidencia.append(f"- Análisis IA de evidencia: {ev.ANALISIS_IA.strip()}")
    if resumenes_evidencia:
        lineas.append("Evidencias del incidente:")
        lineas.extend(resumenes_evidencia)

    if incluir_chat_cliente:
        conversacion_cliente = (
            db.query(CONVERSACIONES)
            .filter(
                CONVERSACIONES.ID_INCIDENTE == incidente.ID_INCIDENTE,
                CONVERSACIONES.TIPO == "CLIENTE",
            )
            .first()
        )
        if conversacion_cliente is not None:
            mensajes_cliente = (
                db.query(MENSAJES_CHAT)
                .filter(MENSAJES_CHAT.ID_CONVERSACION == conversacion_cliente.ID_CONVERSACION)
                .order_by(MENSAJES_CHAT.FECHA_CREACION)
                .all()
            )
            if mensajes_cliente:
                lineas.append("Conversación con el cliente (contexto para el técnico):")
                for m in mensajes_cliente:
                    emisor = _enum_a_texto(m.ROL_EMISOR)
                    contenido = m.CONTENIDO or (
                        "[adjuntó una imagen]" if m.TIPO_ADJUNTO else ""
                    )
                    if contenido:
                        lineas.append(f"- {emisor}: {contenido}")

    return "\n".join(lineas)


def _historial_reciente(db: Session, conversacion: CONVERSACIONES) -> list[MENSAJES_CHAT]:
    mensajes = (
        db.query(MENSAJES_CHAT)
        .filter(MENSAJES_CHAT.ID_CONVERSACION == conversacion.ID_CONVERSACION)
        .order_by(MENSAJES_CHAT.FECHA_CREACION.desc())
        .limit(_MAX_HISTORIAL_MENSAJES)
        .all()
    )
    return list(reversed(mensajes))


def _formatear_historial(mensajes: list[MENSAJES_CHAT]) -> str:
    lineas = []
    for m in mensajes:
        emisor = _enum_a_texto(m.ROL_EMISOR)
        contenido = m.CONTENIDO or ("[adjuntó una imagen]" if m.TIPO_ADJUNTO else "")
        if contenido:
            lineas.append(f"{emisor}: {contenido}")
    return "\n".join(lineas) if lineas else "(sin mensajes previos)"


def generar_respuesta_cliente(
    db: Session,
    incidente: INCIDENTES,
    conversacion: CONVERSACIONES,
    mensaje_usuario: str | None,
    image_part: dict | None = None,
) -> tuple[str, bool]:
    """
    Genera la respuesta de la IA (mecánico especialista) para el hilo del
    cliente. Devuelve (respuesta, relevante_tecnico). Nunca lanza excepción:
    ante cualquier falla, retorna el fallback seguro.
    """
    try:
        contexto = construir_contexto_incidente(db, incidente)
        historial = _formatear_historial(_historial_reciente(db, conversacion))

        prompt = f"""Actuás como un mecánico especialista en emergencias vehiculares que
asiste por chat a un cliente mientras un técnico está en camino.

Reglas:
- Priorizá siempre la seguridad del cliente (SAFETY FIRST): alejarse del tráfico,
  señalización, no manipular partes calientes o eléctricas peligrosas, etc.
- Dá indicaciones prácticas y breves en español mientras espera al técnico.
- Hacé preguntas de seguimiento para recolectar detalles útiles para el técnico.
- NUNCA inventes datos específicos del vehículo que no estén en el contexto.
- Respondé ÚNICAMENTE con un objeto JSON válido, sin texto adicional, con esta forma:
{{
  "respuesta": "string con tu respuesta al cliente",
  "relevante_tecnico": true o false,
  "motivo_relevancia": "string o null"
}}

"relevante_tecnico" debe ser true únicamente si el ÚLTIMO mensaje del cliente
aporta información técnica NUEVA y relevante para el técnico que va en camino
(nuevos síntomas, detalles del daño, cambios en la situación, riesgos de
seguridad). Si es una pregunta genérica o no aporta info nueva, debe ser false.

Contexto del incidente:
{contexto}

Historial reciente de la conversación:
{historial}

Nuevo mensaje del cliente:
{mensaje_usuario or "(el cliente envió un adjunto sin texto)"}
"""

        resultado = run_gemini(prompt=prompt, image_part=image_part)
        respuesta = (resultado.get("respuesta") or "").strip()
        if not respuesta:
            raise ValueError("Respuesta vacía de Gemini")
        relevante = bool(resultado.get("relevante_tecnico", False))
        return respuesta, relevante
    except Exception:
        logger.exception(
            "Fallo generando respuesta de IA (cliente) para incidente %s",
            incidente.ID_INCIDENTE,
        )
        return _FALLBACK_CLIENTE, False


def generar_respuesta_tecnico(
    db: Session,
    incidente: INCIDENTES,
    conversacion: CONVERSACIONES,
    mensaje_usuario: str | None = None,
) -> str:
    """
    Genera la sugerencia/respuesta del copiloto de taller para el técnico
    asignado. Si `mensaje_usuario` es None, es la sugerencia inicial que abre
    la conversación. Nunca lanza excepción: ante cualquier falla retorna un
    fallback seguro.
    """
    try:
        contexto = construir_contexto_incidente(db, incidente, incluir_chat_cliente=True)
        historial = _formatear_historial(_historial_reciente(db, conversacion))

        if mensaje_usuario is None:
            instruccion = (
                "Generá el mensaje de apertura del copiloto: sugerí las herramientas "
                "y repuestos probables para este incidente, con una justificación breve."
            )
            mensaje_seccion = "(apertura automática de la conversación, sin mensaje del técnico)"
        else:
            instruccion = (
                "Respondé la pregunta del técnico usando todo el contexto disponible, "
                "sugiriendo herramientas y/o repuestos cuando sea pertinente."
            )
            mensaje_seccion = mensaje_usuario

        prompt = f"""Actuás como copiloto de taller para un técnico que fue asignado a un
incidente vehicular. Tu trabajo es sugerir herramientas ("herramientas") y
repuestos ("repuestos") probables según la clasificación del incidente, el
diagnóstico disponible, el vehículo y TODO lo conversado en el chat del cliente.

{instruccion}

Sé práctico, concreto y breve. Respondé en español. Respondé ÚNICAMENTE con un
objeto JSON válido, sin texto adicional, con esta forma:
{{
  "respuesta": "string con tu sugerencia o respuesta para el técnico"
}}

Contexto del incidente (incluye la conversación con el cliente):
{contexto}

Historial reciente de la conversación con el técnico:
{historial}

Mensaje del técnico:
{mensaje_seccion}
"""

        resultado = run_gemini(prompt=prompt)
        respuesta = (resultado.get("respuesta") or "").strip()
        if not respuesta:
            raise ValueError("Respuesta vacía de Gemini")
        return respuesta
    except Exception:
        logger.exception(
            "Fallo generando respuesta de IA (técnico) para incidente %s",
            incidente.ID_INCIDENTE,
        )
        return _FALLBACK_TECNICO


def notificar_tecnico_info_relevante(db: Session, incidente_id: int, resumen: str) -> None:
    """
    Notifica al técnico asignado (canal WS del incidente + notificación de
    taller) que el cliente compartió información técnica relevante nueva.
    Best-effort: una falla acá nunca debe romper el flujo del chat.
    """
    try:
        from app.modules.notifications.service import (
            _broadcast_incidente,
            enviar_notificacion_taller,
        )

        payload = {
            "tipo": "chat_info_relevante",
            "id_incidente": incidente_id,
            "mensaje": resumen,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _broadcast_incidente(incidente_id, payload)
        enviar_notificacion_taller(db, incidente_id, resumen)
    except Exception:
        logger.exception(
            "Fallo notificando info relevante del chat al técnico — incidente %s",
            incidente_id,
        )
