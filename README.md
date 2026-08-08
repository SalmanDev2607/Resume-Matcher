# Resume-to-Job Matcher

Scores your resume against a folder of job descriptions and ranks them,
so you know which jobs are worth your time before you apply on LinkedIn,
Naukri, etc.

**Why this doesn't auto-apply for you:** LinkedIn and Naukri don't offer
a public API for submitting applications, and both prohibit login-bot
automation in their terms of service. A bot that logs in and clicks
"Apply" risks getting your account banned. This tool instead handles the
part that's safe to automate — figuring out *which* jobs you're actually
a strong match for and *what's missing* from your resume for each one —
so you can apply faster and smarter, manually.

## Setup (one-time)

```bash
cd resume_matcher
pip install -r requirements.txt
```

To auto-fetch live listings (see "Option A" below), also:
1. Register free at https://developer.adzuna.com/ (takes ~2 minutes)
2. Grab your `app_id` and `app_key` from the dashboard
3. Set them as environment variables so the script can find them:

```bash
export ADZUNA_APP_ID="your_app_id"
export ADZUNA_APP_KEY="your_app_key"
```

(Add those two lines to your `~/.bashrc` so you don't have to re-set them every session.)

## Usage

### Option A — Auto-fetch listings (Indeed, and boards Adzuna aggregates)

```bash
python fetch_jobs.py --what "backend developer node.js" --where "Hyderabad" --pages 2
python main.py --resume /path/to/your_resume.pdf
```

`fetch_jobs.py` pulls live listings from Adzuna's public job-search API
(a legitimate, ToS-compliant API — not scraping) and saves each one as a
file in `job_descriptions/`, ready for `main.py` to score. Run it again
with different `--what`/`--where` to pull more roles.

Note: this can't reach LinkedIn or Naukri directly — neither offers a
public API, and automating logins against them risks getting your
account banned. Adzuna's index does include cross-posted listings from
many boards, but for LinkedIn/Naukri-exclusive postings, use Option B.

### Option B — Paste in listings manually (needed for LinkedIn/Naukri)

1. Save your resume as a `.pdf`, `.docx`, or `.txt` file somewhere.
2. For each job you're considering, copy the full job description text
   and save it as a file inside `job_descriptions/` — one file per job.
   Name the file after the role, e.g.:
   - `job_descriptions/Backend Engineer - Razorpay.txt`
   - `job_descriptions/SDE II - Zomato.pdf`
3. Run:

```bash
python main.py --resume /path/to/your_resume.pdf
```

## What this tool does — and deliberately doesn't

- ✅ Scores your resume against job descriptions (`main.py`)
- ✅ Auto-fetches live listings from a legitimate public jobs API (`fetch_jobs.py`)
- ✅ Tracks every application you make and its status in Excel (`tracker.py`)
- ❌ Does **not** log into LinkedIn or Naukri and click "Apply" for you. Neither
  platform offers a public API for this, and automating logins/clicks against
  them violates their terms of service — real accounts get suspended for it.
  That part stays manual, or use **Claude for Chrome** (Anthropic's browsing
  agent) to do it with you present and approving each step, instead of an
  unattended script holding your password.

## Opening your top matches (`open_top_matches.py`)

Instead of copy-pasting each job URL by hand, this opens your best matches
as browser tabs in your regular, already-logged-in browser — you just click
through and hit Apply on each one yourself:

```bash
python open_top_matches.py --top 5 --min-score 0.3
```

- `--top N` — how many to open (default 5)
- `--min-score` — skip anything below this score (default: no filter)
- Only works for jobs pulled via `fetch_jobs.py` (those files carry an
  `Apply link:` line `main.py` picks up). Manually pasted job descriptions
  don't have a URL to open, so those get listed separately for you to open
  by hand.

This **only opens tabs** — it doesn't log in, click, or fill anything.
Everything past the tab opening is you, on purpose (see the note above).

## Tracking applications (`tracker.py`)

Log an application right after you apply (manually, or via Claude for Chrome):

```bash
python tracker.py add --title "Backend Engineer" --company "Fairground" \
    --platform LinkedIn --url "https://..." --score 0.68
```

See everything you've applied to:

```bash
python tracker.py list
```

See applications that have gone quiet and are worth checking on (no status
update in 14+ days, still "Applied"/"Viewed"):

```bash
python tracker.py stale --days 14
```

Update a status after checking (interactive — lists open applications, you
pick one and give it a new status):

```bash
python tracker.py update
```

This creates/updates `applications.xlsx` in the project folder with columns:
Date Applied, Job Title, Company, Platform, Match Score, Job URL, Status,
Last Updated, Notes. Duplicate applications (same title+company+platform)
are automatically skipped when logging.

**Why status isn't auto-updated:** checking "did I get viewed/rejected" on
LinkedIn/Naukri also requires being logged in as you — same automation risk
as applying. `stale` just surfaces what needs a human glance so you're not
manually re-checking everything on a schedule.


This prints a ranked list to the terminal and writes `match_results.csv`
with the full details (scores + matched skills + missing skills per job).

### Options

```bash
python main.py --resume resume.pdf --jobs-dir job_descriptions --output results.csv --top 10
```

- `--jobs-dir` — folder of job description files (default: `job_descriptions`)
- `--output` — where to save the CSV report (default: `match_results.csv`)
- `--top N` — only print the top N matches to the terminal (CSV always has all of them)

## How scoring works

For each job:
- **Skill overlap** — extracts known tech/domain skills from both your
  resume and the job description (see `skills_db.py`) and computes what
  % of the job's required skills you already have.
- **Semantic similarity** — TF-IDF + cosine similarity between the full
  texts, to catch relevant experience that isn't a literal skill keyword.
- **Combined score** = `0.6 × skill overlap + 0.4 × semantic similarity`

The `missing_skills` column tells you exactly what to mention learning,
or address directly, in your cover letter/application for that role.

## Customizing

- **Add skills**: `skills_db.py` has a plain Python set of terms. Add
  anything specific to your field (frameworks, certifications, domain
  jargon) and it's picked up automatically next run — no other code
  changes needed.
- **Adjust weighting**: in `matcher.py`, change the `0.6` / `0.4` weights
  in `score_job()` if you want skill-matching to matter more or less
  relative to overall phrasing similarity.

## Full workflow

```bash
python fetch_jobs.py --what "backend developer node.js" --where "Hyderabad" --pages 2
python main.py --resume /path/to/your_resume.pdf
python open_top_matches.py --top 5 --min-score 0.3
# ...apply in the tabs that opened...
python tracker.py add --title "..." --company "..." --platform LinkedIn --score 0.68
# ...later...
python tracker.py stale --days 14
python tracker.py update
```

## Possible next steps (not built yet — ask if you want these)

- A small local web UI (drag-and-drop resume + job descriptions) instead
  of the CLI.
- Auto-drafting a tailored cover letter / screening-question answers for
  your top-ranked matches (still leaving the actual submit click to you).
