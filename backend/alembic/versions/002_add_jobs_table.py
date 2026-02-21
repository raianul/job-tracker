"""Add jobs table; link applications to Job by URL; drop job_details

Revision ID: 002
Revises: 001
Create Date: 2025-02-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create jobs table (one row per unique URL)
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("source_domain", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_source_url"), "jobs", ["source_url"], unique=True)

    # 2. Populate jobs from existing job_applications + job_details (one job per unique source_url)
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO jobs (source_url, title, company, description, location, source_domain, created_at)
        SELECT DISTINCT ON (ja.source_url)
            ja.source_url,
            jd.title,
            jd.company,
            jd.description,
            jd.location,
            jd.source_domain,
            CURRENT_TIMESTAMP
        FROM job_applications ja
        LEFT JOIN job_details jd ON jd.job_application_id = ja.id
        ORDER BY ja.source_url, jd.id NULLS LAST
    """))

    # 3. Add job_id and notes to job_applications
    op.add_column("job_applications", sa.Column("job_id", sa.Integer(), nullable=True))
    op.add_column("job_applications", sa.Column("notes", sa.Text(), nullable=True))

    # 4. Set job_id from jobs table
    conn.execute(sa.text("""
        UPDATE job_applications
        SET job_id = (SELECT id FROM jobs WHERE jobs.source_url = job_applications.source_url LIMIT 1)
    """))

    # 5. Copy notes from job_details
    conn.execute(sa.text("""
        UPDATE job_applications
        SET notes = (SELECT notes FROM job_details WHERE job_details.job_application_id = job_applications.id LIMIT 1)
    """))

    # 6. Make job_id NOT NULL (if any row has null, fix: create a job for that url)
    conn.execute(sa.text("""
        INSERT INTO jobs (source_url, created_at)
        SELECT DISTINCT source_url, CURRENT_TIMESTAMP
        FROM job_applications
        WHERE job_id IS NULL
    """))
    conn.execute(sa.text("""
        UPDATE job_applications
        SET job_id = (SELECT id FROM jobs WHERE jobs.source_url = job_applications.source_url LIMIT 1)
        WHERE job_id IS NULL
    """))
    op.alter_column(
        "job_applications",
        "job_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # 7. Drop job_details and source_url
    op.drop_index(op.f("ix_job_details_job_application_id"), table_name="job_details")
    op.drop_table("job_details")
    op.drop_column("job_applications", "source_url")
    op.create_index(op.f("ix_job_applications_job_id"), "job_applications", ["job_id"], unique=False)
    op.create_foreign_key(
        "job_applications_job_id_fkey",
        "job_applications",
        "jobs",
        ["job_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("job_applications_job_id_fkey", "job_applications", type_="foreignkey")
    op.drop_index(op.f("ix_job_applications_job_id"), table_name="job_applications")
    op.add_column("job_applications", sa.Column("source_url", sa.String(2048), nullable=True))
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE job_applications SET source_url = (SELECT source_url FROM jobs WHERE jobs.id = job_applications.job_id)
    """))
    op.alter_column("job_applications", "source_url", nullable=False)
    op.drop_column("job_applications", "job_id")
    op.drop_column("job_applications", "notes")

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

    op.drop_index(op.f("ix_jobs_source_url"), table_name="jobs")
    op.drop_table("jobs")