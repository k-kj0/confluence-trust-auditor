# Confluence Trust Auditor

Confluence tells you when a page was last edited. It doesn't tell you
whether anyone has actually checked the page is still correct. An
untouched page could be perfectly fine, or it could be two reorgs out of
date, and there's no way to tell the difference just by looking.

This tool scans a Confluence space and flags two kinds of pages:

1. Pages that haven't been edited or marked reviewed in a long time.
2. Pages that mention things like passwords, API keys, salary figures, or
   "confidential" notes, the kind of content that probably shouldn't be
   exposed to Rovo or any other AI feature reading across a space.

It writes everything into one HTML report you can open in a browser or
attach to an email.

**Live demo (runs on sample data, no real account needed):**
https://confluence-trust-auditor.vercel.app

This was built around two things people are actually saying in public: an
Atlassian community post called ["Hey, Atlassian! How about fixing some
bugs?"](https://community.developer.atlassian.com/t/hey-atlassian-how-about-fixing-some-bugs/91979)
about small long-standing issues piling up, and ongoing concern about what
Rovo and other AI features can see and reuse from private content.

## What's in this repo

confluence-trust-auditor/
├── main.py the file you actually run
├── requirements.txt two packages: requests, python-dotenv
├── .env.example copy this to .env and fill in your own values
├── auditor/
│ ├── confluence_client.py talks to the real Confluence API, the only
│ file in this repo that makes network calls
│ ├── staleness.py decides if a page counts as stale
│ ├── sensitive_scan.py scans page text for secrets, PII, salary data
│ └── report.py builds the HTML report
├── sample_data/
│ └── sample_pages.json fake pages used by --demo and the live demo
├── tests/
│ └── test_staleness.py a few sanity checks for the scoring logic
├── public/index.html the landing page for the Vercel demo
└── api/demo.py the Vercel function behind the demo button


## Try it with no setup

```bash
pip install -r requirements.txt
python main.py --demo
```

This runs against the sample pages and writes `report.html` in the folder.
Open it in a browser, it's exactly what a real scan produces, just on made
up data.

## Run it against a real Confluence site

1. Get a free Confluence Cloud site at atlassian.com/software/confluence
   if you don't have one already (free plan, up to 10 users, no card).
2. Create an API token at
   https://id.atlassian.com/manage-profile/security/api-tokens
3. Copy `.env.example` to `.env` and fill in your site URL, your login
   email, and the token from step 2.
4. Run it:

```bash
python main.py --space-key YOURKEY
```

Useful flags:
- `--stale-days 90` changes the cutoff from the default 180 days
- `--apply-labels` writes a `needs-review` label back onto stale pages in
  Confluence (off by default, the tool only reads until you add this)
- `--output myreport.html` changes where the report gets saved

## Worth knowing before you rely on this

This doesn't look inside Rovo's actual index. Atlassian doesn't expose
that through the API, so nobody outside Atlassian can check it directly.
What this does instead is flag content that would be a risk if any AI
feature had read access to the space, which is a useful thing to know
before turning one on, but it's not the same claim.

The sensitive content patterns are deliberately broad and will catch some
false positives. That's on purpose. A person reviews the flagged list
before anything happens. Nothing gets auto deleted or auto redacted.
