"""
Pulls live job listings from major job boards using python-jobspy and Adzuna,
and saves each one as a text file in job_descriptions/, ready for main.py to score.

Usage:
    python fetch_jobs.py --search "backend developer node.js" --location "Hyderabad, India" --results 20 --source both
    python main.py --resume your_resume.pdf
"""

import argparse
import os
import re
import sys
import requests
import pandas as pd
from jobspy import scrape_jobs

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", str(name))
    return cleaned.strip()[:150] or "untitled"

def fetch_adzuna_jobs(what, where, country="in", app_id=None, app_key=None, pages=1, results_per_page=20):
    app_id = app_id or os.environ.get("ADZUNA_APP_ID")
    app_key = app_key or os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("Warning: Missing Adzuna credentials. Skipping Adzuna.", file=sys.stderr)
        return []

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
            print("Warning: Adzuna rejected the credentials (401 Unauthorized). Skipping Adzuna.", file=sys.stderr)
            return []
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        all_jobs.extend(results)
    
    # Format Adzuna jobs to match a common dictionary structure
    formatted_jobs = []
    for job in all_jobs:
        formatted_jobs.append({
            "title": job.get("title", "Untitled role"),
            "company": (job.get("company") or {}).get("display_name", "Unknown company"),
            "location": (job.get("location") or {}).get("display_name", ""),
            "description": job.get("description", ""),
            "redirect_url": job.get("redirect_url", ""),
            "source": "Adzuna"
        })
    return formatted_jobs

def fetch_jobspy_jobs(search, location, site_name, results_wanted=20):
    try:
        jobs_df = scrape_jobs(
            site_name=site_name,
            search_term=search,
            location=location,
            results_wanted=results_wanted,
            hours_old=168, # Past week
            country_circa="india", # default to india, but location arg takes precedence
            linkedin_fetch_description=True
        )
        
        if jobs_df.empty:
            return []

        formatted_jobs = []
        for index, job in jobs_df.iterrows():
            title = job.get("title", "Untitled role") if not pd.isna(job.get("title")) else "Untitled role"
            company = job.get("company", "Unknown company") if not pd.isna(job.get("company")) else "Unknown company"
            loc = job.get("location", "") if not pd.isna(job.get("location")) else ""
            desc = job.get("description", "") if not pd.isna(job.get("description")) else ""
            apply_url = job.get("job_url", "") if not pd.isna(job.get("job_url")) else ""
            
            site_val = job.get("site", "JobSpy") if not pd.isna(job.get("site")) else "JobSpy"
            source_name = str(site_val).capitalize()
            
            formatted_jobs.append({
                "title": title,
                "company": company,
                "location": loc,
                "description": desc,
                "redirect_url": apply_url,
                "source": source_name
            })
        return formatted_jobs
    except Exception as e:
        print(f"Warning: JobSpy failed: {e}", file=sys.stderr)
        return []

def fetch_jobs(what, where, pages=1, source="both", experience=""):
    results = []
    results_wanted = pages * 20
    
    # Append experience to search query if provided
    search_query = f"{what} {experience}".strip()
    
    jobspy_sites = ["indeed", "linkedin", "glassdoor", "zip_recruiter"]
    
    if source == "both":
        results.extend(fetch_jobspy_jobs(search_query, where, jobspy_sites, results_wanted))
        results.extend(fetch_adzuna_jobs(search_query, where, pages=pages, results_per_page=20))
    elif source == "adzuna":
        results.extend(fetch_adzuna_jobs(search_query, where, pages=pages, results_per_page=20))
    elif source == "jobspy":
        results.extend(fetch_jobspy_jobs(search_query, where, jobspy_sites, results_wanted))
    elif source in jobspy_sites:
        results.extend(fetch_jobspy_jobs(search_query, where, [source], results_wanted))
        
    return results

def save_jobs_as_files(jobs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    saved_paths = []

    for job in jobs:
        title = job.get("title", "Untitled role")
        company = job.get("company", "Unknown company")
        location = job.get("location", "")
        description = job.get("description", "")
        apply_url = job.get("redirect_url", "")
        source = job.get("source", "Unknown")

        fname = sanitize_filename(f"[{source}] {title} - {company}") + ".txt"
        fpath = os.path.join(out_dir, fname)

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Company: {company}\n")
            f.write(f"Location: {location}\n")
            f.write(f"Source: {source}\n")
            f.write(f"Apply link: {apply_url}\n\n")
            f.write(str(description))

        saved_paths.append(fpath)

    return saved_paths

def main():
    parser = argparse.ArgumentParser(
        description="Fetch live job listings from major job boards and save them as job description files."
    )
    parser.add_argument("--search", required=True, help="Job title/keywords, e.g. 'backend developer node.js'")
    parser.add_argument("--location", default="Hyderabad, India", help="Location (default: 'Hyderabad, India')")
    parser.add_argument("--results", type=int, default=20, help="Number of results to fetch (default: 20)")
    parser.add_argument("--source", default="both", help="Source to fetch jobs from (both, adzuna, jobspy, linkedin, indeed, glassdoor, zip_recruiter)")
    parser.add_argument("--experience", default="", help="Experience level to append to search query")
    parser.add_argument("--out-dir", default="job_descriptions", help="Folder to save job description files into")
    
    args = parser.parse_args()

    print(f"Fetching up to {args.results} jobs for '{args.search} {args.experience}' in '{args.location}' from '{args.source}'...")
    
    pages = max(1, args.results // 20)
    jobs = fetch_jobs(args.search, args.location, pages=pages, source=args.source, experience=args.experience)
    
    print(f"Found {len(jobs)} jobs.")
    if not jobs:
        print("No jobs found for that search.")
        return

    saved = save_jobs_as_files(jobs, args.out_dir)
    print(f"Saved {len(saved)} job description file(s) to {args.out_dir}/")
    print("\nNext: python main.py --resume <your_resume.pdf>")

if __name__ == "__main__":
    main()
