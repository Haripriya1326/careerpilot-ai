"""
recommendation_agent.py
-------------------------
Agent that matches a student's extracted skills against the static job
dataset and produces a ranked list with a match percentage plus the
matched / missing skill breakdown the frontend displays.
"""


def _normalize(skill_string: str) -> set:
    """Turn a comma-separated skill string into a lowercase set for comparison."""
    if not skill_string:
        return set()
    return {s.strip().lower() for s in skill_string.split(",") if s.strip()}


def match_jobs(student_skills: list, jobs: list) -> list:
    """Score every job against the student's skill set and sort best-first.

    student_skills: list of skill strings, e.g. ["Python", "SQL"]
    jobs: list of dicts with at least "skills" (comma-separated string)
    """
    student_skill_set = {s.strip().lower() for s in student_skills}
    ranked_jobs = []

    for job in jobs:
        job_skill_set = _normalize(job.get("skills", ""))

        if not job_skill_set:
            continue

        matched = job_skill_set & student_skill_set
        missing = job_skill_set - student_skill_set

        match_percent = round((len(matched) / len(job_skill_set)) * 100)

        # Preserve original casing for display by mapping back from the job's skill list
        original_case_lookup = {s.strip().lower(): s.strip() for s in job.get("skills", "").split(",") if s.strip()}

        ranked_jobs.append({
            "job_id": job.get("id"),
            "company": job.get("company"),
            "role": job.get("role"),
            "location": job.get("location"),
            "salary": job.get("salary"),
            "link": job.get("link"),
            "match": match_percent,
            "matched_skills": [original_case_lookup[s] for s in matched],
            "missing_skills": [original_case_lookup[s] for s in missing],
        })

    ranked_jobs.sort(key=lambda j: j["match"], reverse=True)
    return ranked_jobs
