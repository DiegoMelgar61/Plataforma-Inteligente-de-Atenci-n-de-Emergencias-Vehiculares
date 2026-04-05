"""
Stubs de integración con modelos de IA (STT, visión, clasificación, resumen).
Sustituir por llamadas reales a APIs (OpenAI, Vertex, modelos locales, etc.).
"""
from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import EVIDENCIAS, INCIDENTES

logger = logging.getLogger(__name__)


def transcribir_audio(ruta_archivo: str) -> str:
    """
    Convierte audio a texto (ej. Whisper).

    :param ruta_archivo: Ruta absoluta o relativa al archivo de audio en disco.
    :return: Transcripción; vacío si el stub no procesa el archivo.
    """
    logger.debug("[STUB] transcribir_audio: %s", ruta_archivo)
    if not ruta_archivo or not Path(ruta_archivo).exists():
        return ""
    return "[STUB] Transcripción no disponible (integrar STT)."


def analizar_imagen_basica(ruta_archivo: str) -> str:
    """
    Análisis visual básico del siniestro (daños, contexto).

    :param ruta_archivo: Ruta al archivo de imagen.
    :return: Descripción corta o etiquetas; vacío si no hay archivo.
    """
    logger.debug("[STUB] analizar_imagen_basica: %s", ruta_archivo)
    if not ruta_archivo or not Path(ruta_archivo).exists():
        return ""
    return "[STUB] Análisis de imagen pendiente (integrar visión)."


def clasificar_incidente(
    *,
    id_incidente: str,
    fragmentos_texto: list[str],
    pistas_imagen: list[str],
) -> str:
    """
    Sugiere categoría del incidente (valores alineados al enum CLASIFICACION del modelo ORM).

    :param id_incidente: UUID del incidente (texto).
    :param fragmentos_texto: Textos unidos (descripción, transcripciones).
    :param pistas_imagen: Salidas de análisis de imagen.
    """
    logger.debug(
        "[STUB] clasificar_incidente id=%s textos=%s pistas=%s",
        id_incidente,
        len(fragmentos_texto),
        len(pistas_imagen),
    )
    return "INCIERTO"


def generar_resumen_ia(
    *,
    id_incidente: str,
    fragmentos_texto: list[str],
    pistas_imagen: list[str],
    clasificacion: str,
) -> str:
    """
    Genera un resumen operativo para despacho / talleres.

    :param clasificacion: Categoría ya inferida (o por defecto).
    """
    logger.debug("[STUB] generar_resumen_ia id=%s", id_incidente)
    return (
        f"[STUB] Resumen automático pendiente. Incidente {id_incidente}, "
        f"clasificación sugerida: {clasificacion}. "
        "Conectar LLM o plantillas según política del negocio."
    )


def ejecutar_pipeline_procesamiento_incidente(db: Session, id_incidente: UUID) -> INCIDENTES | None:
    """
    Orquesta stubs: transcribe audios, analiza imágenes, clasifica y guarda resumen en BD.

    Actualiza ESTADO (EN_PROCESO_IA → CLASIFICADO), CLASIFICACION y RESUMEN_IA.
    """
    inc = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if inc is None:
        return None

    try:
        evidencias = (
            db.query(EVIDENCIAS)
            .filter(EVIDENCIAS.ID_INCIDENTE == id_incidente)
            .order_by(EVIDENCIAS.FECHA_CREACION)
            .all()
        )

        base = Path(settings.UPLOADS_DIR)
        transcripciones: list[str] = []
        pistas_imagen: list[str] = []
        textos: list[str] = []

        inc.ESTADO = "EN_PROCESO_IA"
        db.add(inc)
        db.flush()

        for ev in evidencias:
            tipo = ev.TIPO.value if hasattr(ev.TIPO, "value") else str(ev.TIPO)
            if tipo == "AUDIO" and ev.CLAVE_ARCHIVO:
                ruta = base / ev.CLAVE_ARCHIVO
                if ruta.is_file():
                    t = transcribir_audio(str(ruta))
                    if t:
                        transcripciones.append(t)
                        if ev.TEXTO_TRANSCRITO is None:
                            ev.TEXTO_TRANSCRITO = t
                            db.add(ev)
            elif tipo == "IMAGEN" and ev.CLAVE_ARCHIVO:
                ruta = base / ev.CLAVE_ARCHIVO
                if ruta.is_file():
                    hint = analizar_imagen_basica(str(ruta))
                    if hint:
                        pistas_imagen.append(hint)
            elif tipo == "TEXTO" and ev.TEXTO_TRANSCRITO:
                textos.append(ev.TEXTO_TRANSCRITO)

        sid = str(id_incidente)
        fragmentos = [x for x in textos + transcripciones if x]

        nueva_clase = clasificar_incidente(
            id_incidente=sid,
            fragmentos_texto=fragmentos,
            pistas_imagen=pistas_imagen,
        )
        resumen = generar_resumen_ia(
            id_incidente=sid,
            fragmentos_texto=fragmentos,
            pistas_imagen=pistas_imagen,
            clasificacion=nueva_clase,
        )

        inc.CLASIFICACION = nueva_clase
        inc.RESUMEN_IA = resumen
        inc.ESTADO = "CLASIFICADO"
        db.add(inc)
        db.commit()
        db.refresh(inc)
        return inc
    except Exception:
        logger.exception("Pipeline IA falló para incidente %s", id_incidente)
        db.rollback()
        raise
