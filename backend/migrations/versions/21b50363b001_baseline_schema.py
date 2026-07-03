"""baseline_schema

Revision ID: 21b50363b001
Revises: 
Create Date: 2026-04-05 02:04:43.741707

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '21b50363b001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    from app.core.database import Base
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Downgrade schema."""
    from app.core.database import Base
    import app.models  # noqa: F401

    Base.metadata.drop_all(bind=op.get_bind())
