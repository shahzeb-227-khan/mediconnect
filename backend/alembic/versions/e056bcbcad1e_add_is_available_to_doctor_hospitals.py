"""add is_available to doctor_hospitals

Revision ID: e056bcbcad1e
Revises: d05c9670d579
Create Date: 2026-07-07 17:29:38.420836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e056bcbcad1e'
down_revision: Union[str, Sequence[str], None] = 'd05c9670d579'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_available" not in {
        column["name"] for column in inspector.get_columns("doctor_hospitals")
    }:
        op.add_column(
            "doctor_hospitals",
            sa.Column(
                "is_available",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_available" in {
        column["name"] for column in inspector.get_columns("doctor_hospitals")
    }:
        op.drop_column("doctor_hospitals", "is_available")
