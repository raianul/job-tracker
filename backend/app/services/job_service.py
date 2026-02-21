from sqlalchemy.orm import Session

from app.models.job import Job


def get_or_create_job(
    db: Session,
    *,
    source_url: str,
    title: str | None = None,
    company: str | None = None,
    description: str | None = None,
    location: str | None = None,
    source_domain: str | None = None,
) -> Job:
    """Find existing Job by source_url or create one. No refetch if already exists."""
    source_url = source_url.strip()
    job = db.query(Job).filter(Job.source_url == source_url).first()
    if job:
        # Optionally update if we have newer fetched data (e.g. title was missing)
        if title is not None and job.title != title:
            job.title = title
        if company is not None and job.company != company:
            job.company = company
        if description is not None:
            job.description = description
        if location is not None:
            job.location = location
        if source_domain is not None:
            job.source_domain = source_domain
        db.commit()
        db.refresh(job)
        return job
    job = Job(
        source_url=source_url,
        title=title,
        company=company,
        description=description,
        location=location,
        source_domain=source_domain,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
