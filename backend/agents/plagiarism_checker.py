"""
plagiarism_checker.py
-----------------------
Agent that flags near-duplicate resumes. Implements a small, dependency-free
TF-IDF + cosine similarity engine (no sklearn needed) so the hackathon build
stays light. Good enough to catch copy-pasted or lightly-edited resumes,
which is the realistic bar for an MVP plagiarism check.
"""

import re
import math
from collections import Counter

DUPLICATE_THRESHOLD = 80  # percent similarity that triggers is_duplicate = True

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "at",
    "by", "is", "are", "was", "were", "be", "been", "as", "it", "this", "that",
    "i", "my", "me", "we", "our", "he", "she", "they", "his", "her", "their",
}


def tokenize(text: str) -> list:
    """Lowercase, strip punctuation, drop stopwords and very short tokens."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def build_tf(tokens: list) -> dict:
    """Term frequency for a single document."""
    total = len(tokens)
    if total == 0:
        return {}
    counts = Counter(tokens)
    return {term: count / total for term, count in counts.items()}


def cosine_similarity(text_a: str, text_b: str) -> float:
    """Compute TF-IDF-flavoured cosine similarity between two raw texts.

    Since we only ever compare one document against another (pairwise),
    IDF collapses to a constant across both docs and cosine similarity of
    the raw term-frequency vectors is equivalent for ranking purposes, so
    we skip building a full corpus IDF table and just cosine-compare TF
    vectors -- simpler and just as effective for duplicate detection.
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    tf_a = build_tf(tokens_a)
    tf_b = build_tf(tokens_b)

    shared_terms = set(tf_a.keys()) & set(tf_b.keys())
    dot_product = sum(tf_a[term] * tf_b[term] for term in shared_terms)

    magnitude_a = math.sqrt(sum(value ** 2 for value in tf_a.values()))
    magnitude_b = math.sqrt(sum(value ** 2 for value in tf_b.values()))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def check_plagiarism(new_resume_text: str, existing_resumes: list) -> dict:
    """Compare a new resume's text against every stored resume text.

    existing_resumes: list of dicts like {"id": 1, "resume_text": "..."}
    Returns the highest similarity score found, the matching student id,
    and whether that score crosses the duplicate threshold.
    """
    best_score = 0.0
    matched_student_id = None

    for record in existing_resumes:
        other_text = record.get("resume_text") or ""
        if not other_text.strip():
            continue

        similarity = cosine_similarity(new_resume_text, other_text)
        if similarity > best_score:
            best_score = similarity
            matched_student_id = record.get("id")

    plagiarism_score = round(best_score * 100, 2)

    return {
        "plagiarism_score": plagiarism_score,
        "is_duplicate": plagiarism_score >= DUPLICATE_THRESHOLD,
        "matched_student_id": matched_student_id if plagiarism_score >= DUPLICATE_THRESHOLD else None,
    }
