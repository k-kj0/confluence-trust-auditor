"""
staleness.py

Answers one question per page: "has anyone verified this is still true,
recently enough to trust it?"

This directly targets a named, real complaint in Atlassian's own community:
Confluence pages have no last-verified indicator, only a last-edited date,
so nobody can tell whether an unedited page is still accurate or just
never touched.
"""

from datetime import datetime, timezone

REVIEW_LABEL_PREFIXES = ("reviewed-", "verified-")  # e.g. "reviewed-2026-09"


def _parse_iso(ts: str) -> datetime:
    # Confluence returns ISO 8601 timestamps like 2026-03-14T10:22:31.123Z
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def compute_staleness(page: dict, labels: list[str], stale_days: int) -> dict:
    """
    page must have: id, title, version.createdAt
    Returns a dict describing whether the page is stale and why.
    """
    last_updated = _parse_iso(page["version"]["createdAt"])
    now = datetime.now(timezone.utc)
    days_since_update = (now - last_updated).days

    has_recent_review_label = any(lbl.startswith(REVIEW_LABEL_PREFIXES) for lbl in labels)

    is_stale = days_since_update >= stale_days and not has_recent_review_label

    return {
        "id": page["id"],
        "title": page["title"],
        "days_since_update": days_since_update,
        "has_review_label": has_recent_review_label,
        "is_stale": is_stale,
    }
