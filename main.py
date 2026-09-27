"""
main.py

Run this file. Two modes:

  Demo mode (no Atlassian account needed — for trying it out / screenshots):
      python main.py --demo

  Real mode (against your actual Confluence Cloud site):
      python main.py --space-key ENG

Real mode reads credentials from a .env file (copy .env.example to .env
and fill it in) or from environment variables of the same names.
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from auditor.confluence_client import ConfluenceClient
from auditor.staleness import compute_staleness
from auditor.sensitive_scan import scan_content
from auditor.report import generate_html_report


def run_demo(stale_days: int, output_path: str) -> None:
    with open("sample_data/sample_pages.json") as f:
        data = json.load(f)

    stale_pages, sensitive_pages = [], []
    for page in data["pages"]:
        result = compute_staleness(page, page["labels"], stale_days)
        if result["is_stale"]:
            stale_pages.append(result)

        matches = scan_content(page["body"])
        if matches:
            sensitive_pages.append({"id": page["id"], "title": page["title"], "matches": matches})

    html = generate_html_report(data["space_name"], stale_pages, sensitive_pages)
    with open(output_path, "w") as f:
        f.write(html)

    _print_summary(data["space_name"], stale_pages, sensitive_pages, output_path)


def run_real(space_key: str, stale_days: int, output_path: str, apply_labels: bool) -> None:
    load_dotenv()
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    email = os.environ["CONFLUENCE_EMAIL"]
    api_token = os.environ["CONFLUENCE_API_TOKEN"]

    client = ConfluenceClient(base_url, email, api_token)

    spaces = client.list_spaces()
    space = next((s for s in spaces if s["key"] == space_key), None)
    if not space:
        print(f"No space found with key '{space_key}'. Available keys: "
              f"{[s['key'] for s in spaces]}")
        sys.exit(1)

    pages = client.list_pages(space["id"])
    stale_pages, sensitive_pages = [], []

    for page in pages:
        labels = client.get_page_labels(page["id"])
        result = compute_staleness(page, labels, stale_days)
        if result["is_stale"]:
            stale_pages.append(result)
            if apply_labels:
                client.add_label(page["id"], "needs-review")

        body = client.get_page_body(page["id"])
        matches = scan_content(body)
        if matches:
            sensitive_pages.append({"id": page["id"], "title": page["title"], "matches": matches})

    html = generate_html_report(space["name"], stale_pages, sensitive_pages)
    with open(output_path, "w") as f:
        f.write(html)

    _print_summary(space["name"], stale_pages, sensitive_pages, output_path)


def _print_summary(space_name, stale_pages, sensitive_pages, output_path):
    print(f"\nSpace: {space_name}")
    print(f"Stale/unverified pages:   {len(stale_pages)}")
    print(f"Sensitive-content flags:  {len(sensitive_pages)}")
    print(f"\nFull report written to: {output_path}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confluence Trust Auditor")
    parser.add_argument("--demo", action="store_true", help="Run against bundled sample data, no credentials needed")
    parser.add_argument("--space-key", help="Confluence space key to scan, e.g. ENG")
    parser.add_argument("--stale-days", type=int, default=180, help="Days since last edit before a page is 'stale'")
    parser.add_argument("--output", default="report.html", help="Where to write the HTML report")
    parser.add_argument("--apply-labels", action="store_true",
                         help="Actually write a 'needs-review' label back onto stale pages (real mode only)")
    args = parser.parse_args()

    if args.demo:
        run_demo(args.stale_days, args.output)
    elif args.space_key:
        run_real(args.space_key, args.stale_days, args.output, args.apply_labels)
    else:
        parser.error("Pass either --demo or --space-key SPACEKEY")
