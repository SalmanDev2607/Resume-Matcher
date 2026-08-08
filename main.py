"""
Resume-to-Job Matcher
======================
Scores a resume against a folder of job description files and ranks
them so you know which ones are worth your time to apply to.

Usage:
    python main.py --resume path/to/resume.pdf --jobs-dir job_descriptions

Job description files: drop one file per job (.txt, .pdf, or .docx) into
the jobs-dir folder. The filename (minus extension) is used as the job's
display name, e.g. "Backend Engineer - Razorpay.txt".
"""

import argparse
import os
import re
import sys

import pandas as pd

from extractor import extract_text
from matcher import score_job

_APPLY_URL_RE = re.compile(r"^Apply link:\s*(\S+)", re.IGNORECASE | re.MULTILINE)


def extract_apply_url(jd_text: str) -> str:
    """Pulls the apply URL out of files saved by fetch_jobs.py. Manually
    pasted job descriptions won't have this line, so returns "" for those."""
    match = _APPLY_URL_RE.search(jd_text)
    return match.group(1) if match else ""


def load_job_descriptions(jobs_dir: str) -> dict:
    jobs = {}
    if not os.path.isdir(jobs_dir):
        print(f"Jobs directory not found: {jobs_dir}", file=sys.stderr)
        sys.exit(1)

    for fname in sorted(os.listdir(jobs_dir)):
        fpath = os.path.join(jobs_dir, fname)
        if not os.path.isfile(fpath):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in (".txt", ".md", ".pdf", ".docx"):
            continue
        try:
            text = extract_text(fpath)
            if text.strip():
                job_name = os.path.splitext(fname)[0]
                jobs[job_name] = text
            else:
                print(f"  (skipping {fname} -- no extractable text)")
        except Exception as e:
            print(f"  (skipping {fname} -- {e})")

    return jobs


def main():
    parser = argparse.ArgumentParser(description="Match a resume against job descriptions.")
    parser.add_argument("--resume", required=True, help="Path to your resume (.pdf, .docx, .txt)")
    parser.add_argument("--jobs-dir", default="job_descriptions",
                         help="Folder containing job description files (default: job_descriptions)")
    parser.add_argument("--output", default="match_results.csv",
                         help="Where to write the CSV report (default: match_results.csv)")
    parser.add_argument("--top", type=int, default=None,
                         help="Only show the top N results (default: show all)")
    args = parser.parse_args()

    print(f"Reading resume: {args.resume}")
    resume_text = extract_text(args.resume)
    if not resume_text.strip():
        print("Could not extract any text from the resume. Is the PDF a scanned image?", file=sys.stderr)
        sys.exit(1)

    print(f"Loading job descriptions from: {args.jobs_dir}")
    jobs = load_job_descriptions(args.jobs_dir)
    if not jobs:
        print(f"No job description files found in {args.jobs_dir}. "
              f"Drop .txt/.pdf/.docx files in there (one per job) and re-run.")
        sys.exit(0)
    print(f"Found {len(jobs)} job description(s). Scoring...\n")

    rows = []
    for job_name, jd_text in jobs.items():
        result = score_job(resume_text, jd_text)
        rows.append({
            "job": job_name,
            "match_score": result["combined_score"],
            "skill_overlap_%": result["skill_overlap_pct"],
            "semantic_similarity_%": result["semantic_similarity_pct"],
            "matched_skills": ", ".join(result["matched_skills"]),
            "missing_skills": ", ".join(result["missing_skills"]),
            "apply_url": extract_apply_url(jd_text),
        })

    df = pd.DataFrame(rows).sort_values("match_score", ascending=False).reset_index(drop=True)
    df.index += 1

    display_df = df if args.top is None else df.head(args.top)

    print("=" * 100)
    print("RANKED MATCHES (higher match_score = better fit)")
    print("=" * 100)
    for idx, row in display_df.iterrows():
        print(f"\n#{idx}  {row['job']}")
        print(f"    Match score: {row['match_score']}  "
              f"(skill overlap: {row['skill_overlap_%']}%, similarity: {row['semantic_similarity_%']}%)")
        if row["missing_skills"]:
            print(f"    Missing skills to address in your application: {row['missing_skills']}")

    df.to_csv(args.output, index=True, index_label="rank")
    print(f"\nFull report written to: {args.output}")


if __name__ == "__main__":
    main()
