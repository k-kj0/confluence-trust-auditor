"""
report.py

Turns the results into one self-contained HTML file you can open in a
browser, screenshot, or attach to an email. No JS frameworks, no network
calls, no external files besides two Google Fonts, so it always renders.
"""

from datetime import datetime, timezone

_STYLE = """
:root {
  --paper: #F1F4F1;
  --paper-line: #DAE3DD;
  --surface: #FFFFFF;
  --ink: #142723;
  --ink-soft: #4D625D;
  --teal: #0F6E63;
  --teal-soft: #E3F1EE;
  --flag: #B23A2E;
  --flag-soft: #F9E9E6;
  --stale: #7A5B00;
  --stale-soft: #FBF3D8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 860px; margin: 0 auto; padding: 3.5rem 1.75rem 4rem; }
.masthead {
  display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 2px solid var(--ink); padding-bottom: 1rem; margin-bottom: 2rem;
}
h1 {
  font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.9rem; margin: 0;
}
.ref {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: var(--ink-soft);
  text-align: right; line-height: 1.5;
}
.summary { display: flex; gap: 1rem; margin-bottom: 2.5rem; }
.stat {
  flex: 1; background: var(--surface); border: 1px solid var(--paper-line);
  border-radius: 4px; padding: 1.1rem 1.3rem;
}
.stat .num {
  font-family: 'IBM Plex Mono', monospace; font-size: 2rem; font-weight: 600; line-height: 1;
}
.stat.stale .num { color: var(--stale); }
.stat.flag .num { color: var(--flag); }
.stat .label { color: var(--ink-soft); font-size: 0.88rem; margin-top: 0.35rem; }
section { margin-bottom: 2.75rem; }
h2 { font-size: 1.15rem; margin: 0 0 0.4rem; }
section > p { color: var(--ink-soft); max-width: 66ch; line-height: 1.6; margin: 0 0 1.2rem; }
.ledger { background: var(--surface); border: 1px solid var(--paper-line); border-radius: 4px; overflow: hidden; }
.row {
  display: flex; justify-content: space-between; align-items: center; gap: 1rem;
  padding: 0.85rem 1.25rem; border-bottom: 1px solid var(--paper-line);
}
.row:last-child { border-bottom: none; }
.row .title { font-size: 0.94rem; }
.row .meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end; }
.pageid { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: var(--ink-soft); }
.tag {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; padding: 3px 8px; border-radius: 3px;
  white-space: nowrap;
}
.tag.stale { background: var(--stale-soft); color: var(--stale); }
.tag.flag { background: var(--flag-soft); color: var(--flag); }
.empty { padding: 1.1rem 1.25rem; color: var(--ink-soft); font-size: 0.92rem; }
"""

_HEAD = """<head>
<meta charset="utf-8">
<title>Confluence Trust Report{title_suffix}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>{style}</style>
</head>"""


def _stale_row(p: dict) -> str:
    return (
        f'<div class="row"><span class="title">{p["title"]}</span>'
        f'<span class="meta"><span class="tag stale">{p["days_since_update"]} days untouched</span>'
        f'<span class="pageid">#{p["id"]}</span></span></div>'
    )


def _sensitive_row(p: dict) -> str:
    tags = "".join(f'<span class="tag flag">{m}</span>' for m in p["matches"])
    return (
        f'<div class="row"><span class="title">{p["title"]}</span>'
        f'<span class="meta">{tags}<span class="pageid">#{p["id"]}</span></span></div>'
    )


def generate_html_report(space_name: str, stale_pages: list[dict], sensitive_pages: list[dict]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    stale_body = (
        "".join(_stale_row(p) for p in sorted(stale_pages, key=lambda p: -p["days_since_update"]))
        if stale_pages else '<div class="empty">No stale pages found in this scan.</div>'
    )
    sensitive_body = (
        "".join(_sensitive_row(p) for p in sensitive_pages)
        if sensitive_pages else '<div class="empty">No sensitive-content matches found in this scan.</div>'
    )

    head = _HEAD.format(title_suffix=f": {space_name}", style=_STYLE)

    return f"""<!DOCTYPE html>
<html lang="en">
{head}
<body>
<div class="wrap">

  <div class="masthead">
    <h1>Confluence Trust Report</h1>
    <div class="ref">{space_name}<br>Generated {generated_at}</div>
  </div>

  <div class="summary">
    <div class="stat stale"><div class="num">{len(stale_pages)}</div><div class="label">Stale, unverified pages</div></div>
    <div class="stat flag"><div class="num">{len(sensitive_pages)}</div><div class="label">Pages flagged for sensitive content</div></div>
  </div>

  <section>
    <h2>Stale pages</h2>
    <p>No recent edit and no review label. Nobody currently tells readers whether this content is still accurate. That is the gap this report fills.</p>
    <div class="ledger">{stale_body}</div>
  </section>

  <section>
    <h2>Pages flagged for potentially sensitive content</h2>
    <p>Any AI feature with read access to this space, Rovo or otherwise, could surface this content elsewhere. Review before enabling AI search or answers on this space, or restrict these pages directly.</p>
    <div class="ledger">{sensitive_body}</div>
  </section>

</div>
</body>
</html>"""
