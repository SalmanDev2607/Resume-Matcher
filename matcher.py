"""
Core scoring logic: given resume text and a job description's text,
produce a combined match score plus a list of skills the job wants
that don't show up in the resume.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_db import SKILLS

# Sort once, longest-first, so multi-word skills (e.g. "machine learning")
# are matched before their single-word substrings.
_SORTED_SKILLS = sorted(SKILLS, key=len, reverse=True)


def find_skills(text: str) -> set:
    """Return the set of known skills mentioned in the given text."""
    text_lower = text.lower()
    found = set()
    for skill in _SORTED_SKILLS:
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between resume and job description, 0-1."""
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        # Happens if one of the docs is empty after stop-word removal
        return 0.0
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return float(sim)


def score_job(resume_text: str, jd_text: str) -> dict:
    resume_skills = find_skills(resume_text)
    jd_skills = find_skills(jd_text)

    if jd_skills:
        matched_skills = resume_skills & jd_skills
        missing_skills = jd_skills - resume_skills
        skill_overlap = len(matched_skills) / len(jd_skills)
    else:
        matched_skills, missing_skills, skill_overlap = set(), set(), 0.0

    sim = semantic_similarity(resume_text, jd_text)

    # Weighted blend: skill overlap is a stronger, more literal signal
    # for "am I qualified", semantic similarity captures phrasing/context.
    combined = round(0.6 * skill_overlap + 0.4 * sim, 4)

    return {
        "combined_score": combined,
        "skill_overlap_pct": round(skill_overlap * 100, 1),
        "semantic_similarity_pct": round(sim * 100, 1),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
    }
