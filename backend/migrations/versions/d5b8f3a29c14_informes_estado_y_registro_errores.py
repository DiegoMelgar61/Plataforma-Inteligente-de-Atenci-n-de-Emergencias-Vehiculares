"""informes_estado_y_registro_errores

Convierte `informes_servicio` en la fuente de verdad del estado del informe:
- estado (GENERANDO / LISTO / FALLIDO)
- contenido_ia (JSON de secciones devuelto por la IA, para reconstruir el PDF
  sin volver a llamar a la IA)
- correo_enviado (indicador de envío del informe al cliente)
- error_detalle (registro del fallo de IA, PDF o correo — deja de ser silencioso)
- fecha_generacion (momento en que terminó la generación)
- url_archivo / clave_archivo pasan a nullable (no existen mientras GENERANDO
  o si la generación quedó FALLIDO)

Las filas existentes se marcan LISTO (fueron generadas con éxito).

Revision ID: d5b8f3a29c14
Revises: c4a9e2f17b83
Create Date: 2026-07-05 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d5b8f3a29c14"
down_revision: Union[str, Sequence[str], None] = "c4a9e2f17b83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

estado_informe_enum = postgresql.ENUM(
    "GENERANDO", "LISTO", "FALLIDO", name="estado_informe_enum", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columnas = {col["name"] for col in inspector.get_columns("informes_servicio")}

    estado_informe_enum.create(bind, checkfirst=True)

    if "estado" not in columnas:
        op.add_column(
            "informes_servicio",
            sa.Column(
                "estado",
                estado_informe_enum,
                nullable=False,
                server_default="LISTO",
            ),
        )
        # El default LISTO aplica solo a las filas preexistentes (generadas con
        # éxito); las nuevas se crean explícitamente en GENERANDO desde el código.
        op.alter_column("informes_servicio", "estado", server_default=None)

    if "contenido_ia" not in columnas:
        op.add_column(
            "informes_servicio", sa.Column("contenido_ia", sa.JSON(), nullable=True)
        )

    if "correo_enviado" not in columnas:
        op.add_column(
            "informes_servicio",
            sa.Column(
                "correo_enviado",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

    if "error_detalle" not in columnas:
        op.add_column(
            "informes_servicio", sa.Column("error_detalle", sa.Text(), nullable=True)
        )

    if "fecha_generacion" not in columnas:
        op.add_column(
            "informes_servicio",
            sa.Column("fecha_generacion", sa.DateTime(timezone=True), nullable=True),
        )
        # Para filas preexistentes, la fecha de generación es la de creación.
        op.execute(
            "UPDATE informes_servicio SET fecha_generacion = fecha_creacion "
            "WHERE fecha_generacion IS NULL"
        )

    op.alter_column("informes_servicio", "url_archivo", nullable=True)
    op.alter_column("informes_servicio", "clave_archivo", nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columnas = {col["name"] for col in inspector.get_columns("informes_servicio")}

    # Volver a NOT NULL solo es posible si no quedaron filas sin PDF.
    op.execute("DELETE FROM informes_servicio WHERE url_archivo IS NULL")
    op.alter_column("informes_servicio", "url_archivo", nullable=False)
    op.alter_column("informes_servicio", "clave_archivo", nullable=False)

    for columna in (
        "fecha_generacion",
        "error_detalle",
        "correo_enviado",
        "contenido_ia",
        "estado",
    ):
        if columna in columnas:
            op.drop_column("informes_servicio", columna)

    estado_informe_enum.drop(bind, checkfirst=True)
