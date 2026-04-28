"""add_latitud_longitud_to_talleres

Agrega columnas latitud y longitud (DECIMAL 10,7) a la tabla talleres.
Nullable para no romper registros existentes.

Revision ID: c9e5a2b1d4f8
Revises: a7c3e1f89b42
Create Date: 2026-04-28 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c9e5a2b1d4f8"
down_revision: Union[str, Sequence[str], None] = "a7c3e1f89b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("talleres", sa.Column("latitud", sa.DECIMAL(10, 7), nullable=True))
    op.add_column("talleres", sa.Column("longitud", sa.DECIMAL(10, 7), nullable=True))


def downgrade() -> None:
    op.drop_column("talleres", "longitud")
    op.drop_column("talleres", "latitud")
