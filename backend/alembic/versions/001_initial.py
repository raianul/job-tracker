"""Initial schema: users, job_applications, job_details, interview_sessions, site_settings

Revision ID: 001
Revises:
Create Date: 2025-02-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_id", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_provider_id"), "users", ["provider_id"], unique=False)

    op.create_table(
        "job_applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("applied_at", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="applied"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_applications_user_id"), "job_applications", ["user_id"], unique=False)

    op.create_table(
        "job_details",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_application_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("source_domain", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["job_application_id"], ["job_applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_details_job_application_id"), "job_details", ["job_application_id"], unique=True)

    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_application_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True, server_default="0"),
        sa.ForeignKeyConstraint(["job_application_id"], ["job_applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interview_sessions_job_application_id"), "interview_sessions", ["job_application_id"], unique=False)

    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_site_settings_key"), "site_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_site_settings_key"), table_name="site_settings")
    op.drop_table("site_settings")
    op.drop_index(op.f("ix_interview_sessions_job_application_id"), table_name="interview_sessions")
    op.drop_table("interview_sessions")
    op.drop_index(op.f("ix_job_details_job_application_id"), table_name="job_details")
    op.drop_table("job_details")
    op.drop_index(op.f("ix_job_applications_user_id"), table_name="job_applications")
    op.drop_table("job_applications")
    op.drop_index(op.f("ix_users_provider_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
