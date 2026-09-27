"""
sensitive_scan.py

This targets the OTHER named Atlassian complaint: people are uneasy about
Rovo (and AI features generally) deriving answers from private content,
with no clear per-page control over what gets fed in.

This module doesn't (and can't) inspect Rovo's index directly — Atlassian
doesn't expose that. What it CAN do, honestly: scan page content for
patterns that look like secrets/PII/sensitive business data, so admins
know which pages are a governance risk BEFORE turning on any AI feature
that reads across a space. That's a real, buildable, defensible tool.
"""

import re

# (label shown in report, compiled regex). Patterns are deliberately broad;
# false positives are fine here because a human always reviews the flagged
# list before doing anything — this is a triage tool, not an auto-redactor.
SENSITIVE_PATTERNS = [
    ("possible API key / secret", re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*\S{8,}")),
    ("possible password", re.compile(r"(?i)password\s*[:=]\s*\S+")),
    ("possible private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("possible SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("possible credit card number", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    ("marked confidential/internal-only", re.compile(r"(?i)\b(confidential|internal only|do not share|do not distribute)\b")),
    ("salary/compensation figure", re.compile(r"(?i)\b(salary|compensation)\b.{0,40}\$\s?\d{2,3}[,.]?\d{3}")),
]

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(storage_html: str) -> str:
    """Confluence's 'storage format' is XHTML-ish; a plain tag-strip is enough
    for keyword scanning purposes (we don't need a real DOM here)."""
    return _TAG_RE.sub(" ", storage_html)


def scan_content(storage_html: str) -> list[str]:
    """Returns the list of matched pattern labels (deduplicated), never the
    actual matched text — the report should never leak the secret itself."""
    text = _strip_html(storage_html)
    matches = []
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            matches.append(label)
    return matches
