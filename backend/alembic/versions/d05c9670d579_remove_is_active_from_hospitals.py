"""remove is_active from hospitals

Revision ID: d05c9670d579
Revises: b91e892b1fba
Create Date: 2026-07-07 17:24:51.490760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd05c9670d579'
down_revision: Union[str, Sequence[str], None] = 'b91e892b1fba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_active" in {column["name"] for column in inspector.get_columns("hospitals")}:
        op.drop_column("hospitals", "is_active")


def downgrade() -> None:
    """Downgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_active" not in {column["name"] for column in inspector.get_columns("hospitals")}:
        op.add_column(
            "hospitals",
            sa.Column(
                "is_active",
                sa.BOOLEAN(),
                server_default=sa.text("true"),
                nullable=False,
            ),
        )
