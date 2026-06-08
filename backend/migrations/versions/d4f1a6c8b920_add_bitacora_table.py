"""add_bitacora_table

Crea la tabla `bitacora` para auditoría de acciones de usuarios
(logins, reportes, cancelaciones, cambios de estado, pagos, admin, etc.).

Revision ID: d4f1a6c8b920
Revises: f2b8c3d5e1a7
Create Date: 2026-06-07 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d4f1a6c8b920"
down_revision: Union[str, Sequence[str], None] = "f2b8c3d5e1a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bitacora",
        sa.Column("id_bitacora", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("id_usuario", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id_tenant", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("entidad", sa.String(length=50), nullable=True),
        sa.Column("id_entidad", sa.String(length=64), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["id_usuario"], ["usuarios.id_usuario"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["id_tenant"], ["tenants.id_tenant"]),
    )
    op.create_index("ix_bitacora_fecha_creacion", "bitacora", ["fecha_creacion"])
    op.create_index("ix_bitacora_id_tenant", "bitacora", ["id_tenant"])
    op.create_index("ix_bitacora_id_usuario", "bitacora", ["id_usuario"])


def downgrade() -> None:
    op.drop_index("ix_bitacora_id_usuario", table_name="bitacora")
    op.drop_index("ix_bitacora_id_tenant", table_name="bitacora")
    op.drop_index("ix_bitacora_fecha_creacion", table_name="bitacora")
    op.drop_table("bitacora")
