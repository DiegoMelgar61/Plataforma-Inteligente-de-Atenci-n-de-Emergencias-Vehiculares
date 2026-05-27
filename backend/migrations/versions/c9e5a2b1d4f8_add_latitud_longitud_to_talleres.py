"""add_latitud_longitud_to_talleres

Agrega columnas latitud y longitud (DECIMAL 10,7) a la tabla talleres.
Nullable para no romper registros existentes.

Revision ID: c9e5a2b1d4f8
Revises: a7c3e1f89b42
Create Date: 2026-04-28 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c9e5a2b1d4f8"
down_revision: Union[str, Sequence[str], None] = "a7c3e1f89b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE talleres ADD COLUMN IF NOT EXISTS latitud NUMERIC(10,7)")
    op.execute("ALTER TABLE talleres ADD COLUMN IF NOT EXISTS longitud NUMERIC(10,7)")


def downgrade() -> None:
    op.execute("ALTER TABLE talleres DROP COLUMN IF EXISTS longitud")
    op.execute("ALTER TABLE talleres DROP COLUMN IF EXISTS latitud")
