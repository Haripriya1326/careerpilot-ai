"""
routes/resume.py
------------------
Endpoint that accepts a resume PDF, runs it through the parser + plagiarism
agents, stores the student record, and returns everything the dashboard
needs to render immediately after upload.
"""

import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from agents.resume_parser import parse_resume
from agents.plagiarism_checker import check_plagiarism
from database.database import get_connection

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(
    name: str = Form(...),
    email: str = Form(""),
    resume: UploadFile = File(...),
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    # Save the uploaded file with a unique name to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{resume.filename}"
    saved_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Run the resume through the parsing agent
    try:
        parsed = parse_resume(saved_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}")

    conn = get_connection()
    cursor = conn.cursor()

    # Pull existing resume texts to compare the new one against
    cursor.execute("SELECT id, resume_text FROM students")
    existing_resumes = [dict(row) for row in cursor.fetchall()]

    plagiarism_result = check_plagiarism(parsed["resume_text"], existing_resumes)

    skills_string = ",".join(parsed["skills"])

    cursor.execute("""
        INSERT INTO students (name, email, skills, domain, resume_path, resume_text, plagiarism_score, is_duplicate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        skills_string,
        parsed["domain"],
        saved_path,
        parsed["resume_text"],
        plagiarism_result["plagiarism_score"],
        int(plagiarism_result["is_duplicate"]),
    ))
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()

    return {
        "student_id": student_id,
        "name": name,
        "skills": parsed["skills"],
        "domain": parsed["domain"],
        "plagiarism_score": plagiarism_result["plagiarism_score"],
        "is_duplicate": plagiarism_result["is_duplicate"],
        "matched_student_id": plagiarism_result["matched_student_id"],
    }
