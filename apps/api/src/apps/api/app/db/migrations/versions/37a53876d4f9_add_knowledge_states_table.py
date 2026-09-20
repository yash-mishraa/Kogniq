"""add_knowledge_states_table

Revision ID: 37a53876d4f9
Revises: c3ad36bb186f
Create Date: 2026-09-20 18:12:16.368849

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '37a53876d4f9'
down_revision: str | Sequence[str] | None = 'c3ad36bb186f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE knowledge_states (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            mastery_score REAL NOT NULL,
            last_reviewed_at TEXT,
            next_review_due TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX idx_knowledge_states_user_resource ON knowledge_states(user_id, resource_id)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS knowledge_states")
