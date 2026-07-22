"""
routes/profile.py
-------------------
Endpoint returning a single student's stored profile info for the
Profile page / dashboard header.
"""

from fastapi import APIRouter, HTTPException
from database.database import get_connection

router = APIRouter()


@router.get("/profile/{student_id}")
def get_profile(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, skills, domain, plagiarism_score, is_duplicate FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    profile = dict(row)
    profile["skills"] = profile["skills"].split(",") if profile["skills"] else []
    profile["is_duplicate"] = bool(profile["is_duplicate"])
    return profile
