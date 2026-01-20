"""Add database constraints and composite indexes

Revision ID: 20260120213939
Revises:
Create Date: 2026-01-20 21:39:39.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260120213939"
down_revision: str | None = "20260120000000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add CHECK constraint to reviews.quality
    op.create_check_constraint("check_quality_values", "reviews", "quality IN (0, 2, 3, 5)")

    # Add UNIQUE constraint to learning_stats (user_id, deck_id, date)
    op.create_unique_constraint(
        "uq_user_deck_date", "learning_stats", ["user_id", "deck_id", "date"]
    )

    # Add UNIQUE constraint to decks (user_id, name)
    op.create_unique_constraint("uq_user_deck_name", "decks", ["user_id", "name"])

    # Add composite index on cards (deck_id, next_review)
    op.create_index("ix_cards_deck_next_review", "cards", ["deck_id", "next_review"])

    # Add composite index on cards (deck_id, repetitions)
    op.create_index("ix_cards_deck_repetitions", "cards", ["deck_id", "repetitions"])

    # Add composite index on learning_stats (user_id, deck_id, date)
    op.create_index(
        "ix_learning_stats_user_deck_date", "learning_stats", ["user_id", "deck_id", "date"]
    )

    # Add composite index on reviews (user_id, reviewed_at)
    op.create_index("ix_reviews_user_date", "reviews", ["user_id", "reviewed_at"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_reviews_user_date", "reviews")
    op.drop_index("ix_learning_stats_user_deck_date", "learning_stats")
    op.drop_index("ix_cards_deck_repetitions", "cards")
    op.drop_index("ix_cards_deck_next_review", "cards")

    # Drop constraints
    op.drop_constraint("uq_user_deck_name", "decks", type_="unique")
    op.drop_constraint("uq_user_deck_date", "learning_stats", type_="unique")
    op.drop_constraint("check_quality_values", "reviews", type_="check")
