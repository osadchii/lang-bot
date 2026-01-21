"""Add is_active field to decks table.

Revision ID: 20260121120000
Revises: 20260121000000
Create Date: 2026-01-21

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "20260121120000"
down_revision = "20260121000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decks",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    op.drop_column("decks", "is_active")
