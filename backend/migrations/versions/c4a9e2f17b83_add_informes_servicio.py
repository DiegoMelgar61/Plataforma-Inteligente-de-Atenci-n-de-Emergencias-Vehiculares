"""add_informes_servicio

Crea la tabla `informes_servicio` para persistir el informe de servicio en PDF
generado automáticamente con IA al finalizar un incidente (transición a
ATENDIDO). Un informe por incidente/orden.

Revision ID: c4a9e2f17b83
Revises: b3f7d1c9a204
Create Date: 2026-07-05 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4a9e2f17b83"
down_revision: Union[str, Sequence[str], None] = "b3f7d1c9a204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "informes_servicio" not in existing_tables:
        op.create_table(
            "informes_servicio",
            sa.Column("id_informe", sa.Integer(), primary_key=True),
            sa.Column("id_incidente", sa.Integer(), nullable=False),
            sa.Column("id_tenant", sa.Integer(), nullable=True),
            sa.Column("url_archivo", sa.Text(), nullable=False),
            sa.Column("clave_archivo", sa.Text(), nullable=False),
            sa.Column(
                "generado_por_ia",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["id_incidente"], ["incidentes.id_incidente"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["id_tenant"], ["tenants.id_tenant"]),
            sa.UniqueConstraint("id_incidente", name="uq_informes_servicio_incidente"),
        )
        op.create_index(
            "ix_informes_servicio_id_incidente",
            "informes_servicio",
            ["id_incidente"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "informes_servicio" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("informes_servicio")}
        if "ix_informes_servicio_id_incidente" in indexes:
            op.drop_index(
                "ix_informes_servicio_id_incidente", table_name="informes_servicio"
            )
        op.drop_table("informes_servicio")
