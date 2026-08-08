"""
Pulls live job listings from Adzuna's public Job Search API and saves
each one as a text file in job_descriptions/, ready for main.py to score.

Why Adzuna and not LinkedIn/Naukri: those two don't offer a public API,
and automating logins/scraping against them violates their terms of
service (real risk of account bans). Adzuna is a legitimate job-search
API meant for exactly this kind of use, and it indexes listings from
India (and elsewhere) including many that are cross-posted from other
boards.

One-time setup:
    1. Register free at https://developer.adzuna.com/
    2. Grab your app_id and app_key from the dashboard
    3. Set them as environment variables:
         export ADZUNA_APP_ID="your_app_id"
         export ADZUNA_APP_KEY="your_app_key"
       (or pass --app-id / --app-key directly on the command line)

Usage:
    python fetch_jobs.py --what "backend developer node.js" --where "Hyderabad" --pages 2
    python main.py --resume your_resume.pdf
"""

import argparse
import os
import re
import sys

import requests

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    return cleaned.strip()[:150] or "untitled"


def fetch_jobs(what, where, country="in", app_id=None, app_key=None,
                pages=1, results_per_page=20):
    app_id = app_id or os.environ.get("ADZUNA_APP_ID")
    app_key = app_key or os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError(
            "Missing Adzuna credentials. Register free at "
            "https://developer.adzuna.com/, then set ADZUNA_APP_ID and "
            "ADZUNA_APP_KEY environment variables (or pass --app-id/--app-key)."
        )

    all_jobs = []
    for page in range(1, pages + 1):
        url = f"{ADZUNA_BASE}/{country}/search/{page}"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": what,
            "where": where,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 401:
            raise RuntimeError(
                "Adzuna rejected the credentials (401 Unauthorized). "
                "Double-check ADZUNA_APP_ID / ADZUNA_APP_KEY."
            )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        all_jobs.extend(results)

    return all_jobs


def save_jobs_as_files(jobs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    saved_paths = []

    for job in jobs:
        title = job.get("title", "Untitled role")
        company = (job.get("company") or {}).get("display_name", "Unknown company")
        location = (job.get("location") or {}).get("display_name", "")
        description = job.get("description", "")
        apply_url = job.get("redirect_url", "")

        fname = sanitize_filename(f"{title} - {company}") + ".txt"
        fpath = os.path.join(out_dir, fname)

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Company: {company}\n")
            f.write(f"Location: {location}\n")
            f.write(f"Apply link: {apply_url}\n\n")
            f.write(description)

        saved_paths.append(fpath)

    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Fetch live job listings from Adzuna and save them as job description files."
    )
    parser.add_argument("--what", required=True,
                         help="Job title/keywords, e.g. 'backend developer node.js'")
    parser.add_argument("--where", default="Hyderabad", help="Location (default: Hyderabad)")
    parser.add_argument("--country", default="in",
                         help="Adzuna country code, e.g. in/us/gb (default: in)")
    parser.add_argument("--pages", type=int, default=1,
                         help="Result pages to fetch, ~20 jobs per page (default: 1)")
    parser.add_argument("--out-dir", default="job_descriptions",
                         help="Folder to save job description files into (default: job_descriptions)")
    parser.add_argument("--app-id", default=None, help="Adzuna app_id (or set ADZUNA_APP_ID env var)")
    parser.add_argument("--app-key", default=None, help="Adzuna app_key (or set ADZUNA_APP_KEY env var)")
    args = parser.parse_args()

    print(f"Fetching jobs for '{args.what}' in '{args.where}' (country: {args.country})...")
    try:
        jobs = fetch_jobs(args.what, args.where, args.country,
                           args.app_id, args.app_key, args.pages)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error talking to Adzuna: {e}", file=sys.stderr)
        sys.exit(1)

    if not jobs:
        print("No jobs found for that search. Try broader keywords or a different location.")
        return

    saved = save_jobs_as_files(jobs, args.out_dir)
    print(f"Saved {len(saved)} job description file(s) to {args.out_dir}/")
    print("\nNext: python main.py --resume <your_resume.pdf>")


if __name__ == "__main__":
    main()
