"""
Vercel serverless function. Runs the same scan logic as main.py's --demo
mode, but returns the HTML report as an HTTP response instead of writing
it to a file. Only uses the bundled sample data, never real credentials,
so this is safe to leave public.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auditor.staleness import compute_staleness
from auditor.sensitive_scan import scan_content
from auditor.report import generate_html_report


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample_pages.json")
        with open(sample_path) as f:
            data = json.load(f)

        stale_pages = []
        sensitive_pages = []

        for page in data["pages"]:
            result = compute_staleness(page, page["labels"], stale_days=180)
            if result["is_stale"]:
                stale_pages.append(result)

            matches = scan_content(page["body"])
            if matches:
                sensitive_pages.append({"id": page["id"], "title": page["title"], "matches": matches})

        html = generate_html_report(data["space_name"], stale_pages, sensitive_pages)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
