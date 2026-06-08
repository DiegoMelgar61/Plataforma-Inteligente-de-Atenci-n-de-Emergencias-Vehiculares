"""
Generación de respaldos SQL de la base de datos (dump de datos).

No usa pg_dump (evita depender del binario en la imagen Docker y del pooler de
Supabase): recorre las tablas en orden FK-safe y emite sentencias INSERT. El
resultado se restaura sobre un esquema ya creado por las migraciones de Alembic.
"""
from __future__ import annotations

import datetime as _dt
import decimal
import logging
import uuid
from io import StringIO

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import Base

logger = logging.getLogger(__name__)


def _sql_valor(v) -> str:
    """Serializa un valor Python a literal SQL seguro."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float, decimal.Decimal)):
        return str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return "'\\x" + bytes(v).hex() + "'"
    if isinstance(v, (_dt.datetime, _dt.date, _dt.time)):
        return "'" + v.isoformat() + "'"
    if isinstance(v, uuid.UUID):
        return "'" + str(v) + "'"
    # str y cualquier otro: escapar comillas simples.
    return "'" + str(v).replace("'", "''") + "'"


def generar_dump_sql(db: Session) -> str:
    """Devuelve un script SQL con los INSERT de todas las tablas del modelo."""
    out = StringIO()
    ahora = _dt.datetime.now().isoformat(timespec="seconds")
    out.write("-- Respaldo de datos — Plataforma Emergencias Vehiculares\n")
    out.write(f"-- Generado: {ahora}\n")
    out.write("-- Dump de datos (INSERT). Restaurar sobre el esquema de migraciones.\n")
    out.write("BEGIN;\n\n")

    total_filas = 0
    # sorted_tables: orden seguro por dependencias (padres antes que hijos).
    for tabla in Base.metadata.sorted_tables:
        nombre = tabla.name
        columnas = [c.name for c in tabla.columns]
        try:
            filas = db.execute(text(f'SELECT * FROM "{nombre}"')).fetchall()
        except Exception:
            logger.exception("No se pudo leer la tabla %s para el respaldo", nombre)
            out.write(f"-- (omitida tabla {nombre}: error de lectura)\n\n")
            continue

        out.write(f"-- Tabla: {nombre} ({len(filas)} filas)\n")
        if filas:
            cols_sql = ", ".join(f'"{c}"' for c in columnas)
            for fila in filas:
                valores = ", ".join(_sql_valor(v) for v in fila)
                out.write(f'INSERT INTO "{nombre}" ({cols_sql}) VALUES ({valores});\n')
            total_filas += len(filas)
        out.write("\n")

    out.write("COMMIT;\n")
    logger.info("Respaldo generado: %d filas en %d tablas", total_filas, len(Base.metadata.sorted_tables))
    return out.getvalue()
