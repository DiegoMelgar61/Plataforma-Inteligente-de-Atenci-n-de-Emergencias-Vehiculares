"""add_analisis_ia_to_evidencias

Agrega columna analisis_ia (TEXT nullable) a la tabla evidencias.
Permite almacenar la descripción de daños visibles generada por Gemini
para evidencias de tipo IMAGEN de forma consultable e independiente
del resumen global en INCIDENTES.RESUMEN_IA.

Revision ID: f2b8c3d5e1a7
Revises: c9e5a2b1d4f8
Create Date: 2026-04-28 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f2b8c3d5e1a7"
down_revision: Union[str, Sequence[str], None] = "c9e5a2b1d4f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("evidencias")}
    if "analisis_ia" not in columns:
        op.add_column("evidencias", sa.Column("analisis_ia", sa.Text(), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("evidencias")}
    if "analisis_ia" in columns:
        op.drop_column("evidencias", "analisis_ia")
