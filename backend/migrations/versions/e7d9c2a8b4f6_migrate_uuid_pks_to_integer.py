"""migrate_uuid_pks_to_integer

Migrates all UUID primary keys to sequential INTEGER (auto-increment).
Also migrates foreign-key columns referencing those PKs.

Tables converted: incidentes, usuarios, talleres, tecnicos, asignaciones,
pagos, cotizaciones, bitacora, vehiculos, evidencias.

Revision ID: e7d9c2a8b4f6
Revises: d4f1a6c8b920
Create Date: 2026-07-03 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7d9c2a8b4f6"
down_revision: Union[str, Sequence[str], None] = "d4f1a6c8b920"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_uuid_column(table: str, column: str) -> bool:
    """Check if a column is currently UUID type (UUID, CHAR, or VARCHAR)."""
    inspector = sa.inspect(op.get_bind())
    cols = {c["name"]: str(c["type"]).upper() for c in inspector.get_columns(table)}
    col_type = cols.get(column, "")
    return "UUID" in col_type or "CHAR" in col_type or "VARCHAR" in col_type


def _ensure_sequence(table: str, column: str) -> str:
    """Create a sequence for auto-increment if it doesn't exist. Returns sequence name."""
    seq_name = f"seq_{table}_{column}"
    op.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq_name} OWNED BY {table}.{column}")
    return seq_name


def _table_has_data(table: str) -> bool:
    """Check if a table has any rows."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}"))
    return result.scalar() > 0


def _migrate_pk(table: str, column: str) -> None:
    """Convert a UUID PK column to INTEGER with auto-increment sequence."""
    if not _is_uuid_column(table, column):
        print(f"  SKIP {table}.{column} — already integer or not UUID")
        return

    has_data = _table_has_data(table)
    seq_name = _ensure_sequence(table, column)

    if has_data:
        op.execute(f"""
            ALTER TABLE {table}
            ALTER COLUMN {column} TYPE INTEGER
            USING (
                SELECT nextval('{seq_name}')
                FROM generate_series(1, (SELECT COUNT(*) FROM {table}))
                WHERE {table}.{column} = {table}.{column}
            );
        """)
        op.execute(f"SELECT setval('{seq_name}', (SELECT COALESCE(MAX({column}), 0) FROM {table}))")
    else:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE INTEGER")

    op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT nextval('{seq_name}')")
    op.execute(f"ALTER SEQUENCE {seq_name} OWNED BY {table}.{column}")


def _migrate_fk_column(table: str, column: str) -> None:
    """Convert a UUID FK reference column to INTEGER (no sequence needed)."""
    if not _is_uuid_column(table, column):
        print(f"  SKIP {table}.{column} — already integer or not UUID")
        return
    op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE INTEGER USING {column}::text::integer")


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    # ── Step 1: Drop all FK constraints ────────────────────────────────────
    fk_drops = [
        ("asignaciones", "asignaciones_id_incidente_fkey"),
        ("asignaciones", "asignaciones_id_taller_fkey"),
        ("asignaciones", "asignaciones_id_tecnico_fkey"),
        ("pagos", "pagos_id_incidente_fkey"),
        ("pagos", "pagos_id_taller_fkey"),
        ("pagos", "pagos_id_asignacion_fkey"),
        ("cotizaciones", "cotizaciones_id_incidente_fkey"),
        ("cotizaciones", "cotizaciones_id_taller_fkey"),
        ("cotizaciones", "cotizaciones_id_tecnico_fkey"),
        ("evidencias", "evidencias_id_incidente_fkey"),
        ("tecnicos", "tecnicos_id_usuario_fkey"),
        ("tecnicos", "tecnicos_id_taller_fkey"),
        ("bitacora", "bitacora_id_usuario_fkey"),
        ("vehiculos", "vehiculos_id_usuario_cliente_fkey"),
        ("incidentes", "incidentes_id_usuario_cliente_fkey"),
    ]

    for table, fk_name in fk_drops:
        if table in existing_tables:
            try:
                op.drop_constraint(fk_name, table, type_="foreignkey")
            except Exception:
                print(f"  WARN: could not drop FK {fk_name} on {table}")

    # ── Step 2: Migrate PK columns (creates sequences) ──────────────────────
    pk_migrations = [
        ("incidentes", "id_incidente"),
        ("usuarios", "id_usuario"),
        ("talleres", "id_taller"),
        ("tecnicos", "id_tecnico"),
        ("asignaciones", "id_asignacion"),
        ("pagos", "id_pago"),
        ("cotizaciones", "id_cotizacion"),
        ("bitacora", "id_bitacora_evento"),
        ("vehiculos", "id_vehiculo"),
        ("evidencias", "id_evidencia"),
    ]

    for table, column in pk_migrations:
        if table in existing_tables:
            _migrate_pk(table, column)

    # ── Step 3: Migrate FK columns ──────────────────────────────────────────
    fk_column_migrations = [
        ("incidentes", "id_usuario_cliente"),
        ("asignaciones", "id_incidente"),
        ("asignaciones", "id_taller"),
        ("asignaciones", "id_tecnico"),
        ("pagos", "id_incidente"),
        ("pagos", "id_taller"),
        ("pagos", "id_asignacion"),
        ("cotizaciones", "id_incidente"),
        ("cotizaciones", "id_taller"),
        ("cotizaciones", "id_tecnico_asignado"),
        ("evidencias", "id_incidente"),
        ("tecnicos", "id_usuario"),
        ("tecnicos", "id_taller"),
        ("bitacora", "id_usuario"),
        ("vehiculos", "id_usuario_cliente"),
    ]

    for table, column in fk_column_migrations:
        if table in existing_tables:
            col_info = {c["name"]: str(c["type"]).upper() for c in inspector.get_columns(table)}
            if column in col_info:
                _migrate_fk_column(table, column)

    # ── Step 4: Recreate FK constraints ─────────────────────────────────────
    fk_creates = [
        ("incidentes", "id_usuario_cliente", "usuarios", "id_usuario", "incidentes_id_usuario_cliente_fkey", "CASCADE"),
        ("asignaciones", "id_incidente", "incidentes", "id_incidente", "asignaciones_id_incidente_fkey", "CASCADE"),
        ("asignaciones", "id_taller", "talleres", "id_taller", "asignaciones_id_taller_fkey", "CASCADE"),
        ("asignaciones", "id_tecnico", "tecnicos", "id_tecnico", "asignaciones_id_tecnico_fkey", "SET NULL"),
        ("pagos", "id_incidente", "incidentes", "id_incidente", "pagos_id_incidente_fkey", "CASCADE"),
        ("pagos", "id_taller", "talleres", "id_taller", "pagos_id_taller_fkey", "CASCADE"),
        ("pagos", "id_asignacion", "asignaciones", "id_asignacion", "pagos_id_asignacion_fkey", "SET NULL"),
        ("cotizaciones", "id_incidente", "incidentes", "id_incidente", "cotizaciones_id_incidente_fkey", "CASCADE"),
        ("cotizaciones", "id_taller", "talleres", "id_taller", "cotizaciones_id_taller_fkey", "CASCADE"),
        ("cotizaciones", "id_tecnico_asignado", "tecnicos", "id_tecnico", "cotizaciones_id_tecnico_fkey", "SET NULL"),
        ("evidencias", "id_incidente", "incidentes", "id_incidente", "evidencias_id_incidente_fkey", "CASCADE"),
        ("tecnicos", "id_usuario", "usuarios", "id_usuario", "tecnicos_id_usuario_fkey", "CASCADE"),
        ("tecnicos", "id_taller", "talleres", "id_taller", "tecnicos_id_taller_fkey", "CASCADE"),
        ("bitacora", "id_usuario", "usuarios", "id_usuario", "bitacora_id_usuario_fkey", "SET NULL"),
        ("vehiculos", "id_usuario_cliente", "usuarios", "id_usuario", "vehiculos_id_usuario_cliente_fkey", "CASCADE"),
    ]

    for src_table, src_col, ref_table, ref_col, fk_name, ondelete in fk_creates:
        if src_table in existing_tables and ref_table in existing_tables:
            try:
                op.create_foreign_key(
                    fk_name,
                    src_table, ref_table,
                    [src_col], [ref_col],
                    ondelete=ondelete,
                )
            except Exception as e:
                print(f"  WARN: could not create FK {fk_name}: {e}")


def downgrade() -> None:
    """Reverse UUID→INT migration is destructive; sequence metadata is lost.
    This downgrade only drops the sequences for safety."""
    tables_with_seqs = [
        ("incidentes", "id_incidente"),
        ("usuarios", "id_usuario"),
        ("talleres", "id_taller"),
        ("tecnicos", "id_tecnico"),
        ("asignaciones", "id_asignacion"),
        ("pagos", "id_pago"),
        ("cotizaciones", "id_cotizacion"),
        ("bitacora", "id_bitacora_evento"),
        ("vehiculos", "id_vehiculo"),
        ("evidencias", "id_evidencia"),
    ]
    for table, column in tables_with_seqs:
        seq_name = f"seq_{table}_{column}"
        op.execute(f"DROP SEQUENCE IF EXISTS {seq_name}")

    print("WARN: UUID→INT migration cannot be fully reversed via code.")
    print("Restore from backup or manually ALTER columns back to UUID if needed.")
