"""
routes/recommendations.py
---------------------------
Endpoint that runs the recommendation agent for a given student against
every job in the database and returns the ranked match list.
"""

from fastapi import APIRouter, HTTPException
from database.database import get_connection
from agents.recommendation_agent import match_jobs

router = APIRouter()


@router.get("/recommendations/{student_id}")
def get_recommendations(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student_row = cursor.fetchone()

    if student_row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found.")

    student = dict(student_row)
    student_skills = student["skills"].split(",") if student["skills"] else []

    cursor.execute("SELECT * FROM jobs")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    ranked_jobs = match_jobs(student_skills, jobs)
    return ranked_jobs
