"""Helpers for querying generated document history."""

from __future__ import annotations

from sqlite3 import Connection, Row


VALID_DOC_TYPES = {"resume", "cover_letter"}


def _validate_doc_type(doc_type: str) -> None:
    if doc_type not in VALID_DOC_TYPES:
        raise ValueError(f"Unsupported generated doc type: {doc_type}")


def get_latest_generated_doc(db: Connection, canonical_job_id: str, doc_type: str) -> Row | None:
    """Return the latest generated document row for a job and document type."""
    _validate_doc_type(doc_type)
    return db.execute(
        """
        SELECT *
        FROM generated_docs
        WHERE canonical_job_id = ? AND doc_type = ?
        ORDER BY datetime(generated_at) DESC, id DESC
        LIMIT 1
        """,
        (canonical_job_id, doc_type),
    ).fetchone()


def get_latest_generated_docs(db: Connection, canonical_job_id: str) -> dict[str, Row | None]:
    """Return latest resume and cover-letter rows for a job."""
    return {
        "resume": get_latest_generated_doc(db, canonical_job_id, "resume"),
        "cover_letter": get_latest_generated_doc(db, canonical_job_id, "cover_letter"),
    }


def list_generated_docs(
    db: Connection,
    canonical_job_id: str,
    doc_type: str | None = None,
    limit: int | None = None,
) -> list[Row]:
    """Return generated document history for a job, newest first."""
    if doc_type is not None:
        _validate_doc_type(doc_type)
    if limit is not None and limit < 1:
        raise ValueError("Generated document history limit must be positive.")

    where = ["canonical_job_id = ?"]
    params: list[object] = [canonical_job_id]
    if doc_type is not None:
        where.append("doc_type = ?")
        params.append(doc_type)

    sql = f"""
        SELECT *
        FROM generated_docs
        WHERE {' AND '.join(where)}
        ORDER BY datetime(generated_at) DESC, id DESC
    """
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return db.execute(sql, params).fetchall()
