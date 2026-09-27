"""
confluence_client.py

Thin wrapper around the real Confluence Cloud REST API (v2).
This is the ONLY file that talks to the network. Everything else in this
project works on plain Python dicts, so it's easy to test without hitting
a live Confluence site (see main.py --demo).

Auth: Confluence Cloud uses Basic Auth with your email + an API token
(NOT your password). Create a token at:
https://id.atlassian.com/manage-profile/security/api-tokens
"""

import base64
import time
import requests


class ConfluenceClient:
    def __init__(self, base_url: str, email: str, api_token: str, timeout: int = 20):
        # base_url looks like: https://yourcompany.atlassian.net/wiki
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        token = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_body: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, headers=self.headers, json=json_body, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def list_spaces(self) -> list[dict]:
        """Returns all spaces on the site (id, key, name)."""
        spaces, cursor = [], None
        while True:
            params = {"limit": 100}
            if cursor:
                params["cursor"] = cursor
            data = self._get("/api/v2/spaces", params=params)
            spaces.extend(data.get("results", []))
            next_link = data.get("_links", {}).get("next")
            if not next_link:
                break
            cursor = next_link.split("cursor=")[-1]
            time.sleep(0.1)  # be polite to the API
        return spaces

    def list_pages(self, space_id: str) -> list[dict]:
        """Returns all pages in a space with id, title, version metadata."""
        pages, cursor = [], None
        while True:
            params = {"limit": 100}
            if cursor:
                params["cursor"] = cursor
            data = self._get(f"/api/v2/spaces/{space_id}/pages", params=params)
            pages.extend(data.get("results", []))
            next_link = data.get("_links", {}).get("next")
            if not next_link:
                break
            cursor = next_link.split("cursor=")[-1]
            time.sleep(0.1)
        return pages

    def get_page_body(self, page_id: str) -> str:
        """Returns the page's rendered storage-format HTML body (raw text search target)."""
        data = self._get(f"/api/v2/pages/{page_id}", params={"body-format": "storage"})
        return data.get("body", {}).get("storage", {}).get("value", "")

    def get_page_labels(self, page_id: str) -> list[str]:
        data = self._get(f"/api/v2/pages/{page_id}/labels")
        return [lbl["name"] for lbl in data.get("results", [])]

    def add_label(self, page_id: str, label_name: str) -> None:
        """Writes a label back onto the page, e.g. 'needs-review'."""
        self._post(f"/api/v2/pages/{page_id}/labels", json_body={"name": label_name})
