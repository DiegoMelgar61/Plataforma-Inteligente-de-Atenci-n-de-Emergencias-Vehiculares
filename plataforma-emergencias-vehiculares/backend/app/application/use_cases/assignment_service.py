"""
Motor de Asignación Inteligente + Sistema de Priorización.
Calcula prioridades según clasificación IA, busca talleres candidatos usando PostGIS,
y asigna automáticamente al taller más cercano con técnico disponible.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import and_, func, text
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.models.models import INCIDENTES, TALLERES, TECNICOS, ASIGNACIONES

logger = logging.getLogger(__name__)

# Mapeo de clasificación IA a prioridad
PRIORIDAD_POR_CLASIFICACION = {
    "CHOQUE": "ALTA",
    "MOTOR": "ALTA",
    "BATERIA": "MEDIA",
    "LLANTA": "MEDIA",
    "OTROS": "BAJA",
    "INCIERTO": "BAJA",
}

# Radio de búsqueda en km para PostGIS
RADIO_BUSQUEDA_KM = 50


def calcular_prioridad(incidente: INCIDENTES) -> str:
    """
    Calcula la prioridad del incidente según su clasificación IA.

    :param incidente: Modelo ORM del incidente
    :return: Nivel de prioridad ("ALTA", "MEDIA", "BAJA")
    """
    clasificacion = incidente.CLASIFICACION
    if clasificacion:
        clasificacion_str = (
            clasificacion.value if hasattr(clasificacion, "value") else str(clasificacion)
        )
        return PRIORIDAD_POR_CLASIFICACION.get(clasificacion_str, "BAJA")
    return "BAJA"


def buscar_talleres_candidatos(db: Session, incidente: INCIDENTES) -> list[dict]:
    """
    Busca talleres con técnicos disponibles dentro del radio de búsqueda,
    usando ST_DWithin de PostGIS para distancia real.

    :param db: Sesión de base de datos
    :param incidente: Modelo ORM del incidente
    :return: Lista de diccionarios con {id_taller, id_tecnico, distancia_km, taller}
    """
    if incidente.UBICACION is None:
        logger.warning("Incidente %s sin ubicación", incidente.ID_INCIDENTE)
        return []

    try:
        # Obtener punto del incidente
        punto_incidente = to_shape(incidente.UBICACION)
        lat_incidente = punto_incidente.y
        lon_incidente = punto_incidente.x

        # Query PostGIS: encontrar talleres y técnicos en radio de búsqueda
        query = db.query(
            TALLERES.ID_TALLER,
            TECNICOS.ID_TECNICO,
            func.ST_Distance(
                func.ST_GeographyFromText(
                    text(f"'POINT({lon_incidente} {lat_incidente})'")
                ),
                TECNICOS.UBICACION_ACTUAL,
                False,
            )
            / 1000.0,  # Distancia en km
        ).join(
            TECNICOS, TALLERES.ID_TALLER == TECNICOS.ID_TALLER
        ).filter(
            TALLERES.ACTIVO.is_(True),
            TECNICOS.DISPONIBLE.is_(True),
            func.ST_DWithin(
                func.ST_GeographyFromText(
                    text(f"'POINT({lon_incidente} {lat_incidente})'")
                ),
                TECNICOS.UBICACION_ACTUAL,
                RADIO_BUSQUEDA_KM * 1000,  # Convertir a metros
            ),
        ).order_by(
            func.ST_Distance(
                func.ST_GeographyFromText(
                    text(f"'POINT({lon_incidente} {lat_incidente})'")
                ),
                TECNICOS.UBICACION_ACTUAL,
                False,
            )
        ).all()

        candidatos = []
        for id_taller, id_tecnico, distancia_km in query:
            taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()
            candidatos.append({
                "id_taller": id_taller,
                "id_tecnico": id_tecnico,
                "distancia_km": float(distancia_km),
                "taller": taller,
            })

        # Fallback: si nadie tiene ubicación registrada, incluir cualquier técnico disponible
        if not candidatos:
            logger.info(
                "Sin candidatos por ubicación para %s, usando fallback sin distancia",
                incidente.ID_INCIDENTE,
            )
            query_fallback = (
                db.query(TALLERES.ID_TALLER, TECNICOS.ID_TECNICO)
                .join(TECNICOS, TALLERES.ID_TALLER == TECNICOS.ID_TALLER)
                .filter(
                    TALLERES.ACTIVO.is_(True),
                    TECNICOS.DISPONIBLE.is_(True),
                )
                .all()
            )
            for id_taller, id_tecnico in query_fallback:
                taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()
                candidatos.append({
                    "id_taller": id_taller,
                    "id_tecnico": id_tecnico,
                    "distancia_km": 0.0,
                    "taller": taller,
                })

        logger.debug(
            "Encontrados %d candidatos para incidente %s",
            len(candidatos),
            incidente.ID_INCIDENTE,
        )
        return candidatos

    except Exception as e:
        logger.exception("Error al buscar talleres candidatos para %s", incidente.ID_INCIDENTE)
        return []


def asignar_taller_automaticamente(db: Session, incidente_id: UUID) -> ASIGNACIONES | None:
    """
    Busca el taller más cercano con técnico disponible y asigna automáticamente.
    Actualiza el estado del incidente a "ASIGNADO".

    :param db: Sesión de base de datos
    :param incidente_id: UUID del incidente
    :return: Objeto ASIGNACIONES creado, o None si no hay candidatos
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        logger.warning("Incidente %s no encontrado", incidente_id)
        return None

    # Actualizar prioridad si es necesario
    nueva_prioridad = calcular_prioridad(incidente)
    if incidente.PRIORIDAD != nueva_prioridad:
        incidente.PRIORIDAD = nueva_prioridad
        db.add(incidente)
        db.flush()

    # Buscar candidatos
    candidatos = buscar_talleres_candidatos(db, incidente)
    if not candidatos:
        logger.warning("No hay talleres candidatos para incidente %s", incidente_id)
        return None

    # Seleccionar el más cercano (ya ordenado por distancia)
    candidato_elegido = candidatos[0]
    id_taller = candidato_elegido["id_taller"]
    id_tecnico = candidato_elegido["id_tecnico"]
    distancia_km = candidato_elegido["distancia_km"]

    try:
        # Crear asignación
        asignacion = ASIGNACIONES(
            ID_INCIDENTE=incidente_id,
            ID_TALLER=id_taller,
            ID_TECNICO=id_tecnico,
        )
        db.add(asignacion)

        # Actualizar estado del incidente a "ASIGNADO"
        incidente.ESTADO = "ASIGNADO"
        db.add(incidente)

        db.commit()
        db.refresh(asignacion)

        # Marcar técnico como no disponible
        tecnico = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == id_tecnico).first()
        if tecnico:
            tecnico.DISPONIBLE = False
            db.add(tecnico)
            db.commit()

        logger.info(
            "Incidente %s asignado a taller %s (distancia: %.2f km)",
            incidente_id,
            id_taller,
            distancia_km,
        )
        return asignacion

    except Exception as e:
        logger.exception("Error al asignar incidente %s", incidente_id)
        db.rollback()
        return None
