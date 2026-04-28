"""add_tecnico_role_and_user_link

Agrega el valor 'TECNICO' al enum rol_enum de PostgreSQL y la columna
id_usuario (FK a usuarios) en la tabla tecnicos para vincular cada
técnico a una cuenta de login con hash seguro.

Revision ID: a7c3e1f89b42
Revises: 21b50363b001
Create Date: 2026-04-27 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "a7c3e1f89b42"
down_revision: Union[str, Sequence[str], None] = "21b50363b001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL ≥ 9.5: ADD VALUE IF NOT EXISTS es atómico y seguro.
    # En versiones < 12 no puede ejecutarse dentro de un bloque de transacción;
    # en v12+ funciona correctamente en transacciones.  El servidor objetivo
    # debe ser PostgreSQL 12 o superior.
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TYPE rol_enum ADD VALUE IF NOT EXISTS 'TECNICO'"))

    # Columna nullable: los técnicos existentes sin cuenta de login quedan con NULL.
    op.add_column(
        "tecnicos",
        sa.Column("id_usuario", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_tecnicos_id_usuario",
        "tecnicos",
        "usuarios",
        ["id_usuario"],
        ["id_usuario"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_tecnicos_id_usuario", "tecnicos", ["id_usuario"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_tecnicos_id_usuario", "tecnicos", type_="unique")
    op.drop_constraint("fk_tecnicos_id_usuario", "tecnicos", type_="foreignkey")
    op.drop_column("tecnicos", "id_usuario")
    # PostgreSQL no permite eliminar valores de un tipo ENUM; la reversión
    # del valor 'TECNICO' requeriría recrear el tipo manualmente.
