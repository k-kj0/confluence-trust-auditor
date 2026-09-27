"""
report.py

Turns the results into one self-contained HTML file you can open in a
browser, screenshot, or attach to an email. No JS frameworks, no network
calls — just a plain page so it always renders, everywhere.
"""

from datetime import datetime, timezone

_STYLE = """
body { font-family: -apple-system, Arial, sans-serif; margin: 2rem; color: #1b1f23; }
h1 { margin-bottom: 0; }
.subtitle { color: #6a737d; margin-top: 4px; }
.summary { display: flex; gap: 1.5rem; margin: 1.5rem 0 2rem; }
.card { border: 1px solid #d0d7de; border-radius: 8px; padding: 1rem 1.5rem; }
.card .num { font-size: 1.8rem; font-weight: 700; }
table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
th, td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; font-size: 0.9rem; }
th { background: #f6f8fa; }
.tag { display: inline-block; background: #ffebe9; color: #82071e; border-radius: 4px;
       padding: 2px 6px; font-size: 0.75rem; margin: 2px; }
.tag.stale { background: #fff8c5; color: #7d5b00; }
"""


def generate_html_report(space_name: str, stale_pages: list[dict], sensitive_pages: list[dict]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    stale_rows = "\n".join(
        f"<tr><td>{p['title']}</td><td>{p['days_since_update']} days</td>"
        f"<td>{p['id']}</td></tr>"
        for p in sorted(stale_pages, key=lambda p: -p["days_since_update"])
    ) or "<tr><td colspan='3'>None found 🎉</td></tr>"

    sensitive_rows = "\n".join(
        f"<tr><td>{p['title']}</td>"
        f"<td>{' '.join(f'<span class=\"tag\">{m}</span>' for m in p['matches'])}</td>"
        f"<td>{p['id']}</td></tr>"
        for p in sensitive_pages
    ) or "<tr><td colspan='3'>None found 🎉</td></tr>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Confluence Trust Report — {space_name}</title>
<style>{_STYLE}</style></head>
<body>
<h1>Confluence Trust Report</h1>
<div class="subtitle">Space: {space_name} · Generated {generated_at}</div>

<div class="summary">
  <div class="card"><div class="num">{len(stale_pages)}</div>Stale, unverified pages</div>
  <div class="card"><div class="num">{len(sensitive_pages)}</div>Pages flagged for sensitive content</div>
</div>

<h2>⏱ Stale pages (no recent edit or review label)</h2>
<p>These pages haven't been edited or marked reviewed recently. Nobody currently
tells readers whether this content is still accurate — that's the gap this
report fills.</p>
<table><tr><th>Page</th><th>Days since last update</th><th>Page ID</th></tr>
{stale_rows}</table>

<h2>🔒 Pages flagged for potentially sensitive content</h2>
<p>Any AI feature with read access to this space (Rovo or otherwise) could
surface this content elsewhere. Review before enabling AI search/answers
on this space, or restrict these pages.</p>
<table><tr><th>Page</th><th>Flag(s)</th><th>Page ID</th></tr>
{sensitive_rows}</table>

</body></html>"""
