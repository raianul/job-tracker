"""Add notes to interview_sessions

Revision ID: 003
Revises: 002
Create Date: 2026-02-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("interview_sessions", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("interview_sessions", "notes")
