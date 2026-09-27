import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auditor.staleness import compute_staleness  # noqa: E402


def _iso_days_ago(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def test_old_unreviewed_page_is_stale():
    page = {"id": "1", "title": "Old Page", "version": {"createdAt": _iso_days_ago(400)}}
    result = compute_staleness(page, labels=[], stale_days=180)
    assert result["is_stale"] is True


def test_old_page_with_review_label_is_not_stale():
    page = {"id": "2", "title": "Reviewed Page", "version": {"createdAt": _iso_days_ago(400)}}
    result = compute_staleness(page, labels=["reviewed-2026-09"], stale_days=180)
    assert result["is_stale"] is False


def test_recent_page_is_not_stale():
    page = {"id": "3", "title": "New Page", "version": {"createdAt": _iso_days_ago(5)}}
    result = compute_staleness(page, labels=[], stale_days=180)
    assert result["is_stale"] is False


if __name__ == "__main__":
    test_old_unreviewed_page_is_stale()
    test_old_page_with_review_label_is_not_stale()
    test_recent_page_is_not_stale()
    print("All tests passed.")
