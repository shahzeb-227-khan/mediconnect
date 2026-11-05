"""add is_active to hospitals

Revision ID: b91e892b1fba
Revises: 4d38992a5163
Create Date: 2026-07-07 16:42:49.723508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b91e892b1fba'
down_revision: Union[str, Sequence[str], None] = '4d38992a5163'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_active" not in {column["name"] for column in inspector.get_columns("hospitals")}:
        op.add_column(
            "hospitals",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    inspector = sa.inspect(op.get_bind())
    if "is_active" in {column["name"] for column in inspector.get_columns("hospitals")}:
        op.drop_column("hospitals", "is_active")
