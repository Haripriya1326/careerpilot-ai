"""
database.py
------------
Handles the SQLite connection and table creation for CareerPilot AI.
"""

import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "careerpilot.db")


def get_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist yet, and seed static job listings."""
    conn = get_connection()
    cursor = conn.cursor()

    # ===========================
    # STUDENTS TABLE
    # ===========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            skills TEXT,
            domain TEXT,
            resume_path TEXT,
            resume_text TEXT,
            plagiarism_score REAL DEFAULT 0,
            is_duplicate INTEGER DEFAULT 0
        )
    """)

    # ===========================
    # USERS TABLE (NEW)
    # ===========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ===========================
    # JOBS TABLE
    # ===========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            skills TEXT,
            domain TEXT,
            location TEXT,
            salary TEXT,
            link TEXT
        )
    """)

    conn.commit()

    # Seed jobs only once
    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]

    if job_count == 0:
        seed_jobs(cursor)
        conn.commit()

    conn.close()


def seed_jobs(cursor):
    """Insert demo job listings."""

    sample_jobs = [
        ("NimbusTech", "Frontend Intern", "HTML,CSS,JavaScript,React", "Web Development", "Remote", "3.5 LPA", "https://example.com/jobs/nimbus-frontend"),
        ("DataForge Labs", "Data Analyst Intern", "Python,SQL,Excel,Pandas", "Data Science", "Bengaluru", "4 LPA", "https://example.com/jobs/dataforge-analyst"),
        ("CloudPeak Systems", "Backend Developer", "Python,FastAPI,SQL,Docker", "Backend Development", "Hyderabad", "6 LPA", "https://example.com/jobs/cloudpeak-backend"),
        ("PixelCraft Studio", "UI/UX Designer", "Figma,CSS,HTML,Design Systems", "Design", "Remote", "4.5 LPA", "https://example.com/jobs/pixelcraft-uiux"),
        ("Quantify AI", "Machine Learning Intern", "Python,Machine Learning,TensorFlow,NumPy", "Data Science", "Pune", "5 LPA", "https://example.com/jobs/quantify-ml"),
        ("Ironclad Security", "Cybersecurity Analyst", "Networking,Linux,Python,Security", "Cybersecurity", "Chennai", "5.5 LPA", "https://example.com/jobs/ironclad-security"),
        ("Skyline Mobile", "Android Developer Intern", "Java,Kotlin,Android,SQL", "Mobile Development", "Remote", "4 LPA", "https://example.com/jobs/skyline-android"),
        ("Vertex Cloud", "DevOps Engineer", "Docker,Kubernetes,AWS,Linux,CI/CD", "Cloud & DevOps", "Bengaluru", "7 LPA", "https://example.com/jobs/vertex-devops"),
        ("BrightPath EdTech", "Full Stack Developer", "JavaScript,React,Node.js,MongoDB", "Web Development", "Remote", "6.5 LPA", "https://example.com/jobs/brightpath-fullstack"),
        ("Lumen Analytics", "Business Intelligence Intern", "SQL,Power BI,Excel,Python", "Data Science", "Mumbai", "3.8 LPA", "https://example.com/jobs/lumen-bi"),
    ]

    cursor.executemany("""
        INSERT INTO jobs
        (company, role, skills, domain, location, salary, link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_jobs)