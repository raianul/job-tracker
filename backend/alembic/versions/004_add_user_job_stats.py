"""Add user job stats (total_applied, total_rejected, total_success)

Revision ID: 004
Revises: 003
Create Date: 2026-02-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("total_applied", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("total_rejected", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("total_success", sa.Integer(), nullable=False, server_default="0"))

    # Backfill from job_applications
    op.execute(sa.text("""
        UPDATE users SET
            total_applied = (SELECT COUNT(*) FROM job_applications WHERE job_applications.user_id = users.id),
            total_rejected = (SELECT COUNT(*) FROM job_applications WHERE job_applications.user_id = users.id AND job_applications.status = 'rejected'),
            total_success = (SELECT COUNT(*) FROM job_applications WHERE job_applications.user_id = users.id AND job_applications.status = 'got_offer')
    """))


def downgrade() -> None:
    op.drop_column("users", "total_success")
    op.drop_column("users", "total_rejected")
    op.drop_column("users", "total_applied")
