"""
routes/jobs.py
----------------
Read-only endpoint exposing the static (seeded) job dataset.
"""

from fastapi import APIRouter
from database.database import get_connection

router = APIRouter()


@router.get("/jobs")
def get_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs
