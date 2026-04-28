"""
Integracion de IA para clasificacion de incidentes vehiculares.

Este modulo:
- arma un prompt estructurado para Gemini,
- procesa evidencia de texto/audio/imagen,
- normaliza la respuesta al dominio interno (enums),
- aplica fallback seguro si falla la IA.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.application.use_cases.assignment_service import asignar_taller_automaticamente
from app.core.config import settings
from app.models.models import EVIDENCIAS, HISTORIAL_INCIDENTES, INCIDENTES

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - fallback si dependencia no esta instalada
    genai = None

logger = logging.getLogger(__name__)

_ALLOWED_CLASIFICACION = {"BATERIA", "LLANTA", "CHOQUE", "MOTOR", "OTROS", "INCIERTO"}
_ALLOWED_PRIORIDAD = {"ALTA", "MEDIA", "BAJA"}

_PROMPT = """Analiza este incidente vehicular y responde UNICAMENTE con un objeto JSON valido, sin texto adicional.

El JSON debe contener exactamente:
{
  "transcripcion_audio": "string o null",
  "clasificacion": "Bateria descargada | Llanta pinchada | Choque frontal | Motor sobrecalentado | Otros",
  "nivel_confianza": 0.0,
  "resultado_imagen": "string o null",
  "prioridad": "alta | normal | baja",
  "resumen_automatico": "2-3 oraciones utiles para el tecnico",
  "recomendaciones": "acciones puntuales para atender el incidente"
}

Reglas de prioridad:
- alta: peligro inmediato (accidente, humo, incendio, perdida de control, frenos)
- normal: no se puede circular seguro, sin riesgo vital inmediato
- baja: falla menor sin riesgo de seguridad

Descripcion del cliente:
{descripcion}

Tipo declarado (si existe):
{tipo_declarado}

Instrucciones de medios:
{instrucciones_medios}
"""


def _enum_to_text(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clean_json(raw: str) -> dict:
    text = (raw or "").strip()
    if "```" in text:
        for chunk in text.split("```"):
            chunk = chunk.strip()
            if chunk.startswith("json"):
                chunk = chunk[4:].strip()
            if chunk.startswith("{") and chunk.endswith("}"):
                text = chunk
                break
    return json.loads(text)


def _normalize_clasificacion(raw: str | None) -> str:
    s = (raw or "").strip().upper()
    if not s:
        return "INCIERTO"

    if "CHOQUE" in s or "COLISION" in s or "IMPACT" in s:
        return "CHOQUE"
    if "MOTOR" in s or "SOBRECAL" in s or "TEMPERAT" in s:
        return "MOTOR"
    if "LLANTA" in s or "NEUMATIC" in s or "PINCH" in s:
        return "LLANTA"
    if "BATER" in s or "BATERIA" in s:
        return "BATERIA"
    if "OTRO" in s:
        return "OTROS"

    return s if s in _ALLOWED_CLASIFICACION else "INCIERTO"


def _normalize_prioridad(raw: str | None) -> str:
    s = (raw or "").strip().upper()
    if not s:
        return "MEDIA"

    if s in {"ALTA", "HIGH"}:
        return "ALTA"
    if s in {"NORMAL", "MEDIA", "MEDIUM"}:
        return "MEDIA"
    if s in {"BAJA", "LOW"}:
        return "BAJA"
    return "MEDIA"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _build_prompt(
    descripcion: str,
    tipo_declarado: str | None,
    has_audio: bool,
    has_image: bool,
) -> str:
    instrucciones = []
    if has_audio:
        instrucciones.append(
            "Se adjunta audio del cliente. Transcribelo literalmente en 'transcripcion_audio'."
        )
    else:
        instrucciones.append("No hay audio; usar null en 'transcripcion_audio'.")

    if has_image:
        instrucciones.append(
            "Se adjunta imagen. Describe danos visibles en 'resultado_imagen'."
        )
    else:
        instrucciones.append("No hay imagen; usar null en 'resultado_imagen'.")

    return _PROMPT.format(
        descripcion=(descripcion or "").strip() or "Sin descripcion textual.",
        tipo_declarado=tipo_declarado or "No especificado.",
        instrucciones_medios=" ".join(instrucciones),
    )


def _run_gemini(
    *,
    prompt: str,
    audio_part: dict | None,
    image_part: dict | None,
) -> dict:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no configurada")
    if genai is None:
        raise RuntimeError("google-generativeai no instalado")

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    parts: list = []
    if audio_part:
        parts.append(audio_part)
    if image_part:
        parts.append(image_part)
    parts.append(prompt)

    response = model.generate_content(
        parts,
        generation_config={"temperature": 0.2},
    )
    raw = (response.text or "").strip()
    return _clean_json(raw)


def _extract_media_parts(
    *,
    evidencias: list[EVIDENCIAS],
    uploads_dir: Path,
) -> tuple[list[str], dict | None, dict | None]:
    """
    Devuelve:
    - textos libres detectados
    - parte audio para Gemini (si existe)
    - parte imagen para Gemini (si existe)
    """
    textos: list[str] = []
    audio_part = None
    image_part = None

    for ev in evidencias:
        tipo = _enum_to_text(ev.TIPO)

        if tipo == "TEXTO" and ev.TEXTO_TRANSCRITO:
            textos.append(ev.TEXTO_TRANSCRITO.strip())
            continue

        if not ev.CLAVE_ARCHIVO:
            continue

        ruta = uploads_dir / ev.CLAVE_ARCHIVO
        if not ruta.is_file():
            continue

        if tipo == "AUDIO" and audio_part is None:
            data = ruta.read_bytes()
            mime = "audio/mpeg"
            ext = ruta.suffix.lower()
            if ext == ".wav":
                mime = "audio/wav"
            elif ext == ".ogg":
                mime = "audio/ogg"
            elif ext in {".m4a", ".mp4"}:
                mime = "audio/mp4"
            elif ext == ".webm":
                mime = "audio/webm"
            audio_part = {"mime_type": mime, "data": data}
            continue

        if tipo == "IMAGEN" and image_part is None:
            data = ruta.read_bytes()
            mime = "image/jpeg"
            ext = ruta.suffix.lower()
            if ext == ".png":
                mime = "image/png"
            elif ext == ".webp":
                mime = "image/webp"
            elif ext == ".gif":
                mime = "image/gif"
            image_part = {"mime_type": mime, "data": data}

    return textos, audio_part, image_part


def _fallback_result(textos: list[str]) -> dict:
    resumen_base = "Incidente recibido. Sin analisis IA completo, requiere revision manual."
    if textos:
        joined = " ".join(textos)[:400]
        resumen_base = f"Reporte cliente: {joined}"
    return {
        "transcripcion_audio": None,
        "clasificacion": "INCIERTO",
        "nivel_confianza": 0.0,
        "resultado_imagen": None,
        "prioridad": "MEDIA",
        "resumen_automatico": resumen_base,
        "recomendaciones": "Contactar al cliente y validar danos in situ antes de intervenir.",
    }


def ejecutar_pipeline_procesamiento_incidente(db: Session, id_incidente: UUID) -> INCIDENTES | None:
    """
    Pipeline IA real con fallback:
    1) recupera evidencias
    2) consulta Gemini multimodal
    3) normaliza salida
    4) persiste clasificacion/resumen/estado/historial
    5) dispara asignacion automatica
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if incidente is None:
        return None

    try:
        evidencias = (
            db.query(EVIDENCIAS)
            .filter(EVIDENCIAS.ID_INCIDENTE == id_incidente)
            .order_by(EVIDENCIAS.FECHA_CREACION)
            .all()
        )
        uploads = Path(settings.UPLOADS_DIR)
        textos, audio_part, image_part = _extract_media_parts(evidencias=evidencias, uploads_dir=uploads)

        incidente.ESTADO = "EN_PROCESO_IA"
        db.add(incidente)
        db.flush()

        prompt = _build_prompt(
            descripcion="\n".join(textos),
            tipo_declarado=_enum_to_text(incidente.CLASIFICACION),
            has_audio=audio_part is not None,
            has_image=image_part is not None,
        )

        try:
            ai_raw = _run_gemini(prompt=prompt, audio_part=audio_part, image_part=image_part)
        except Exception:
            logger.exception("Gemini fallo para incidente %s; aplicando fallback", id_incidente)
            ai_raw = _fallback_result(textos)

        clasificacion = _normalize_clasificacion(ai_raw.get("clasificacion"))
        prioridad = _normalize_prioridad(ai_raw.get("prioridad"))
        confianza = max(0.0, min(1.0, _safe_float(ai_raw.get("nivel_confianza"), 0.0)))
        resumen = (ai_raw.get("resumen_automatico") or "").strip()
        recomendaciones = (ai_raw.get("recomendaciones") or "").strip()
        transcripcion = ai_raw.get("transcripcion_audio")
        analisis_imagen = ai_raw.get("resultado_imagen")

        # Persistir transcripcion en la primera evidencia de audio.
        if isinstance(transcripcion, str) and transcripcion.strip():
            for ev in evidencias:
                if _enum_to_text(ev.TIPO) == "AUDIO":
                    ev.TEXTO_TRANSCRITO = transcripcion.strip()
                    db.add(ev)
                    break

        # Persistir análisis de imagen en la evidencia IMAGEN correspondiente.
        if isinstance(analisis_imagen, str) and analisis_imagen.strip():
            for ev in evidencias:
                if _enum_to_text(ev.TIPO) == "IMAGEN":
                    ev.ANALISIS_IA = analisis_imagen.strip()
                    db.add(ev)
                    break

        detalle_resumen = resumen or "Analisis IA sin resumen textual."
        if recomendaciones:
            detalle_resumen = f"{detalle_resumen}\nRecomendaciones: {recomendaciones}"
        if isinstance(analisis_imagen, str) and analisis_imagen.strip():
            detalle_resumen = f"{detalle_resumen}\nDanos visibles: {analisis_imagen.strip()}"
        detalle_resumen = f"{detalle_resumen}\nConfianza IA: {confianza:.2f}"

        incidente.CLASIFICACION = clasificacion
        incidente.PRIORIDAD = prioridad if prioridad in _ALLOWED_PRIORIDAD else "MEDIA"
        incidente.RESUMEN_IA = detalle_resumen
        incidente.ESTADO = "CLASIFICADO"
        db.add(incidente)

        db.add(
            HISTORIAL_INCIDENTES(
                ID_INCIDENTE=id_incidente,
                ESTADO="CLASIFICADO",
                NOTAS="Clasificacion automatica por IA completada.",
                ID_USUARIO_CAMBIO=None,
            )
        )
        db.commit()
        db.refresh(incidente)

        try:
            logger.info("Iniciando asignacion automatica para incidente %s", id_incidente)
            asignar_taller_automaticamente(db, id_incidente)
        except Exception:
            logger.exception("Asignacion automatica fallo para incidente %s", id_incidente)

        return incidente
    except Exception:
        logger.exception("Pipeline IA fallo para incidente %s", id_incidente)
        db.rollback()
        raise
