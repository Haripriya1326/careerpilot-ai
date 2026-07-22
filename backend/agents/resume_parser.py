"""
resume_parser.py
------------------
Agent responsible for reading a resume PDF and pulling out structured
signal from it: raw text, a skill list (keyword matching) and a predicted
domain (rule-based scoring). Kept dependency-free besides PyMuPDF so it is
easy to reason about during a hackathon demo.
"""

import fitz  # PyMuPDF

# Master skill vocabulary the extractor looks for inside resume text.
# Grouped loosely by area only for readability -- matching itself is flat.
SKILL_LIBRARY = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C", "Kotlin", "Swift", "Go", "R",
    "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Firebase", "SQLite",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NumPy", "Pandas", "Scikit-learn",
    "Data Analysis", "Data Visualization", "Power BI", "Excel", "Tableau",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "CI/CD", "Git", "DevOps",
    "Figma", "UI/UX", "Design Systems", "Photoshop",
    "Networking", "Security", "Cybersecurity",
    "Android", "iOS",
    "Machine Learning", "NLP", "Computer Vision",
]

# Rule-based domain prediction: each domain owns a set of "signal" skills.
# Domain with the highest overlap against the extracted skills wins.
DOMAIN_RULES = {
    "Web Development": {"HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask"},
    "Data Science": {"Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NumPy", "Pandas",
                      "Scikit-learn", "Data Analysis", "Data Visualization", "Power BI", "Tableau", "NLP", "Computer Vision"},
    "Backend Development": {"Python", "Java", "SQL", "FastAPI", "Django", "Flask", "Node.js", "MongoDB", "PostgreSQL"},
    "Mobile Development": {"Kotlin", "Swift", "Android", "iOS", "Java"},
    "Cloud & DevOps": {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "DevOps", "Linux"},
    "Design": {"Figma", "UI/UX", "Design Systems", "Photoshop", "CSS"},
    "Cybersecurity": {"Networking", "Security", "Cybersecurity", "Linux"},
}


def extract_text_from_pdf(file_path: str) -> str:
    """Read all text out of a PDF resume using PyMuPDF."""
    text_chunks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks)


def extract_skills(resume_text: str) -> list:
    """Keyword-match the resume text against the skill library (case-insensitive)."""
    lowered_text = resume_text.lower()
    found_skills = []

    for skill in SKILL_LIBRARY:
        if skill.lower() in lowered_text and skill not in found_skills:
            found_skills.append(skill)

    return found_skills


def predict_domain(skills: list) -> str:
    """Score every domain by how many of its signal skills the student has, pick the best."""
    if not skills:
        return "Unclassified"

    skill_set = set(skills)
    best_domain = "Unclassified"
    best_score = 0

    for domain, signal_skills in DOMAIN_RULES.items():
        overlap = len(skill_set & signal_skills)
        if overlap > best_score:
            best_score = overlap
            best_domain = domain

    return best_domain


def parse_resume(file_path: str):
    resume_text = extract_text_from_pdf(file_path)

    print("\n========== RESUME TEXT ==========")
    print(resume_text)
    print("=================================\n")

    skills = extract_skills(resume_text)

    print("Skills:", skills)

    domain = predict_domain(skills)

    print("Domain:", domain)

    return {
        "resume_text": resume_text,
        "skills": skills,
        "domain": domain,
    }
