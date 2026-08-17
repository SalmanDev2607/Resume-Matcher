import re
import os
import json

# Try to import Gemini AI, but don't fail if not installed properly
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Hardcoded Heuristic Dictionaries
ACTION_VERBS = [
    "achieved", "improved", "trained", "mentored", "managed", "created", 
    "resolved", "volunteered", "influenced", "increased", "decreased", 
    "negotiated", "launched", "revenue", "profit", "orchestrated", "spearheaded",
    "developed", "designed", "implemented", "optimized", "streamlined", "reduced"
]

CLICHES = [
    "team player", "hard worker", "go-getter", "think outside the box", 
    "synergy", "detail-oriented", "results-driven", "dynamic", "self-starter",
    "track record"
]

def score_resume_heuristic(text: str) -> dict:
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    score = 100
    strengths = []
    mistakes = []
    
    # 1. Length Check
    if word_count < 250:
        score -= 20
        mistakes.append(f"Resume is very short ({word_count} words). Aim for at least 300-400 words.")
    elif word_count > 1200:
        score -= 10
        mistakes.append(f"Resume is very long ({word_count} words). Consider trimming to be more concise.")
    else:
        strengths.append(f"Good length ({word_count} words).")
        
    # 2. Contact Info (Email and Phone)
    has_email = "@" in text
    has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)) or bool(re.search(r'\b\d{10}\b', text))
    
    if has_email and has_phone:
        strengths.append("Contains contact information (Email and Phone).")
    else:
        if not has_email:
            score -= 10
            mistakes.append("Missing email address.")
        if not has_phone:
            score -= 5
            mistakes.append("Missing phone number.")
            
    # 3. Quantifiable Metrics (%, $, numbers)
    has_percent = "%" in text
    has_dollar = "$" in text
    # basic check for digits 10-999 to represent metrics, excluding years
    has_numbers = bool(re.search(r'\b([1-9][0-9]{1,3})\b', text))
    
    if has_percent or has_dollar or has_numbers:
        strengths.append("Good use of numbers and quantifiable metrics.")
    else:
        score -= 15
        mistakes.append("Lacks quantifiable metrics. Try to include percentages, money amounts, or concrete numbers to prove your impact.")
        
    # 4. Action Verbs
    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    if len(found_verbs) > 5:
        strengths.append(f"Strong use of action verbs ({len(found_verbs)} found).")
    elif len(found_verbs) > 0:
        score -= 5
        mistakes.append("Could use more strong action verbs (found a few).")
    else:
        score -= 15
        mistakes.append("Missing strong action verbs (e.g., developed, managed, improved).")
        
    # 5. Cliches
    found_cliches = [c for c in CLICHES if c in text_lower]
    if found_cliches:
        score -= 5 * len(found_cliches)
        mistakes.append(f"Contains cliches or buzzwords to avoid: {', '.join(found_cliches)}.")
    else:
        strengths.append("Avoided common cliches and buzzwords.")
        
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "strengths": strengths,
        "mistakes": mistakes,
        "engine": "HEURISTIC"
    }


def score_resume_ai(text: str, api_key: str) -> dict:
    try:
        genai.configure(api_key=api_key)
        # Use gemini-3.5-flash as requested
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        prompt = f"""
You are an expert technical recruiter and resume reviewer.
Analyze the following resume text. Evaluate it on clarity, impact, use of metrics, and formatting.
Provide a score from 0 to 100. Provide a list of 2-4 strengths. Provide a list of 2-4 mistakes or areas for improvement.
Return ONLY valid JSON exactly in this format, with no markdown code blocks or extra text:
{{
    "score": 85,
    "strengths": ["string", "string"],
    "mistakes": ["string", "string"]
}}

RESUME TEXT:
{text}
"""
        response = model.generate_content(prompt)
        # Clean up if the model wrapped it in markdown
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text)
        
        return {
            "score": data.get("score", 70),
            "strengths": data.get("strengths", []),
            "mistakes": data.get("mistakes", []),
            "engine": "AI_GEMINI"
        }
    except Exception as e:
        print(f"AI Scoring failed: {e}")
        return None


def get_resume_score(text: str) -> dict:
    engine_pref = os.environ.get("SCORER_ENGINE", "HEURISTIC").upper()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if engine_pref == "AI" and api_key and HAS_GEMINI:
        ai_result = score_resume_ai(text, api_key)
        if ai_result:
            return ai_result
        print("Falling back to Heuristic engine due to AI failure.")
        
    # Fallback or preferred
    return score_resume_heuristic(text)
