"""
Opens your top-matched jobs as browser tabs in your regular, already-logged-in
browser -- so you can just click through and hit Apply on each, instead of
copy-pasting links one by one.

This does NOT log in, click anything, or fill any forms. It only opens tabs.
Everything after that is you.

Usage:
    python open_top_matches.py --results match_results.csv --top 5 --min-score 0.3
"""

import argparse
import time
import webbrowser

import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Open your top job matches as browser tabs."
    )
    parser.add_argument("--results", default="match_results.csv",
                         help="CSV produced by main.py (default: match_results.csv)")
    parser.add_argument("--top", type=int, default=5,
                         help="How many top matches to open (default: 5)")
    parser.add_argument("--min-score", type=float, default=0.0,
                         help="Skip jobs below this match_score (default: 0.0, i.e. no filter)")
    parser.add_argument("--delay", type=float, default=0.6,
                         help="Seconds to wait between opening each tab, "
                              "so the browser doesn't choke on opening many at once (default: 0.6)")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.results)
    except FileNotFoundError:
        print(f"Couldn't find {args.results}. Run main.py first to generate it.")
        return

    df = df.sort_values("match_score", ascending=False)
    df = df[df["match_score"] >= args.min_score]

    has_url = df["apply_url"].notna() & (df["apply_url"].astype(str).str.strip() != "")
    with_links = df[has_url].head(args.top)
    without_links = df[~has_url].head(args.top)

    if with_links.empty:
        print("None of your top matches have a saved apply link.")
        if not without_links.empty:
            print("(Links are only saved for jobs pulled via fetch_jobs.py -- "
                  "manually pasted job descriptions don't carry a URL.)")
        return

    print(f"Opening {len(with_links)} tab(s) in your default browser...\n")
    for i, (_, row) in enumerate(with_links.iterrows()):
        print(f"  [{row['match_score']:.2f}] {row['job']}")
        webbrowser.open_new_tab(row["apply_url"])
        if i < len(with_links) - 1:
            time.sleep(args.delay)

    if not without_links.empty:
        print(f"\n{len(without_links)} other top match(es) had no saved link "
              f"(manually pasted JDs) -- you'll need to open those yourself:")
        for _, row in without_links.iterrows():
            print(f"  [{row['match_score']:.2f}] {row['job']}")


if __name__ == "__main__":
    main()
