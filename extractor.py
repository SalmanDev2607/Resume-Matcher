"""
Handles pulling plain text out of resume/job-description files,
regardless of whether they're .pdf, .docx, or .txt.
"""

import os


def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext == ".docx":
        return _extract_docx(filepath)
    elif ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(
            f"Unsupported file type '{ext}' for {filepath}. "
            "Use .pdf, .docx, .txt, or .md."
        )


def _extract_pdf(filepath: str) -> str:
    import pdfplumber

    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(filepath: str) -> str:
    import docx

    doc = docx.Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs)
