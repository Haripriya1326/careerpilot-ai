"""
main.py
--------
CareerPilot AI backend entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import init_db

from routes import auth
from routes import login      # NEW
from routes import resume
from routes import jobs
from routes import recommendations
from routes import profile

app = FastAPI(title="CareerPilot AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database and tables
init_db()

# Register all API routes
app.include_router(auth.router)
app.include_router(login.router)      # NEW
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(recommendations.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {
        "message": "CareerPilot AI Backend Running"
    }