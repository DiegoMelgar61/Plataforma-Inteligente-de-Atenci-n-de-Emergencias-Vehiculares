"""add_chat_conversaciones_mensajes

Crea las tablas `conversaciones` y `mensajes_chat` para el chat de IA por
incidente: hilo del cliente (mecánico de emergencias) e hilo del técnico
asignado (copiloto de taller), conectados por un puente de contexto.

Revision ID: b3f7d1c9a204
Revises: e7d9c2a8b4f6
Create Date: 2026-07-05 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b3f7d1c9a204"
down_revision: Union[str, Sequence[str], None] = "e7d9c2a8b4f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_conversacion_enum = postgresql.ENUM(
    "CLIENTE", "TECNICO", name="tipo_conversacion_enum", create_type=False
)
rol_emisor_enum = postgresql.ENUM(
    "CLIENTE", "TECNICO", "IA", name="rol_emisor_enum", create_type=False
)
tipo_adjunto_enum = postgresql.ENUM(
    "IMAGEN", "ARCHIVO", name="tipo_adjunto_enum", create_type=False
)


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    bind = op.get_bind()
    tipo_conversacion_enum.create(bind, checkfirst=True)
    rol_emisor_enum.create(bind, checkfirst=True)
    tipo_adjunto_enum.create(bind, checkfirst=True)

    if "conversaciones" not in existing_tables:
        op.create_table(
            "conversaciones",
            sa.Column("id_conversacion", sa.Integer(), primary_key=True),
            sa.Column("id_incidente", sa.Integer(), nullable=False),
            sa.Column("tipo", tipo_conversacion_enum, nullable=False),
            sa.Column("id_tenant", sa.Integer(), nullable=True),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["id_incidente"], ["incidentes.id_incidente"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["id_tenant"], ["tenants.id_tenant"]),
            sa.UniqueConstraint(
                "id_incidente", "tipo", name="uq_conversaciones_incidente_tipo"
            ),
        )
        op.create_index(
            "ix_conversaciones_id_incidente", "conversaciones", ["id_incidente"]
        )

    if "mensajes_chat" not in existing_tables:
        op.create_table(
            "mensajes_chat",
            sa.Column("id_mensaje", sa.Integer(), primary_key=True),
            sa.Column("id_conversacion", sa.Integer(), nullable=False),
            sa.Column("rol_emisor", rol_emisor_enum, nullable=False),
            sa.Column("id_usuario_emisor", sa.Integer(), nullable=True),
            sa.Column("contenido", sa.Text(), nullable=True),
            sa.Column("url_adjunto", sa.Text(), nullable=True),
            sa.Column("clave_adjunto", sa.Text(), nullable=True),
            sa.Column("tipo_adjunto", tipo_adjunto_enum, nullable=True),
            sa.Column(
                "relevante_tecnico",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["id_conversacion"],
                ["conversaciones.id_conversacion"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["id_usuario_emisor"], ["usuarios.id_usuario"]),
        )
        op.create_index(
            "ix_mensajes_chat_id_conversacion", "mensajes_chat", ["id_conversacion"]
        )
        op.create_index(
            "ix_mensajes_chat_conversacion_fecha",
            "mensajes_chat",
            ["id_conversacion", "fecha_creacion"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "mensajes_chat" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("mensajes_chat")}
        if "ix_mensajes_chat_conversacion_fecha" in indexes:
            op.drop_index("ix_mensajes_chat_conversacion_fecha", table_name="mensajes_chat")
        if "ix_mensajes_chat_id_conversacion" in indexes:
            op.drop_index("ix_mensajes_chat_id_conversacion", table_name="mensajes_chat")
        op.drop_table("mensajes_chat")

    if "conversaciones" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("conversaciones")}
        if "ix_conversaciones_id_incidente" in indexes:
            op.drop_index("ix_conversaciones_id_incidente", table_name="conversaciones")
        op.drop_table("conversaciones")

    bind = op.get_bind()
    tipo_adjunto_enum.drop(bind, checkfirst=True)
    rol_emisor_enum.drop(bind, checkfirst=True)
    tipo_conversacion_enum.drop(bind, checkfirst=True)
