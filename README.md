# CareerPilot AI — Multi-Agent Career Recommendation Platform

A hackathon MVP that takes a student's resume (PDF), extracts skills,
predicts a career domain, checks it against previously uploaded resumes for
duplication, and recommends jobs from a seeded dataset with a match score.

## Tech stack

- **Backend:** Python 3.11, FastAPI, SQLite, PyMuPDF
- **Frontend:** Plain HTML/CSS/JS (no frameworks)

## Project structure

```
backend/
├── agents/
│   ├── resume_parser.py        # PDF text extraction, skill + domain detection
│   ├── recommendation_agent.py # Skill-to-job matching
│   └── plagiarism_checker.py   # Pure-python TF-IDF cosine similarity
├── routes/
│   ├── resume.py                # POST /upload-resume
│   ├── jobs.py                  # GET /jobs
│   ├── recommendations.py       # GET /recommendations/{id}
│   └── profile.py               # GET /profile/{id}
├── database/
│   └── database.py              # SQLite schema + seeded job dataset
├── uploads/                     # Uploaded resume PDFs land here
├── main.py                      # FastAPI app, CORS, router wiring
└── requirements.txt

frontend/
├── index.html      # Sign-in
├── dashboard.html  # Upload + skills + plagiarism gauge + recommendations
├── profile.html    # Stored student profile
├── styles.css      # Custom "flight instrument panel" design system
└── script.js       # Fetch calls + rendering logic
```

## How to run

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API starts on `http://localhost:8000`. A SQLite file
(`backend/database/careerpilot.db`) is created automatically on first run,
along with 10 seeded demo job listings.

Check it's alive:

```bash
curl http://localhost:8000
# {"message": "CareerPilot AI Backend Running"}
```

### 2. Frontend

Just open `frontend/index.html` directly in a browser (double-click it, or
right-click → Open With → your browser). No build step, no server required.

> If your browser blocks `fetch` calls from a `file://` page, serve the
> frontend folder instead:
> ```bash
> cd frontend
> python3 -m http.server 5500
> ```
> then visit `http://localhost:5500`.

## API reference

| Method | Endpoint                  | Description                                   |
|--------|----------------------------|------------------------------------------------|
| GET    | `/`                        | Health check                                   |
| POST   | `/upload-resume`           | Upload a PDF resume (form fields: `name`, `email`, `resume`) |
| GET    | `/jobs`                    | List the seeded job dataset                    |
| GET    | `/recommendations/{id}`    | Ranked job matches for a student                |
| GET    | `/profile/{id}`            | Stored profile for a student                    |

### Example upload response

```json
{
  "student_id": 1,
  "name": "Aditi Sharma",
  "skills": ["Python", "SQL", "FastAPI"],
  "domain": "Backend Development",
  "plagiarism_score": 12.4,
  "is_duplicate": false,
  "matched_student_id": null
}
```

## How each feature works

- **Skill extraction:** keyword matching against a curated skill vocabulary
  in `agents/resume_parser.py`.
- **Domain prediction:** rule-based — each domain owns a set of "signal"
  skills; the domain with the highest overlap wins.
- **Plagiarism detection:** a dependency-free TF-IDF-style cosine similarity
  between the new resume's text and every resume already stored. Scores
  ≥ 80% are flagged as a duplicate (`agents/plagiarism_checker.py`).
- **Job recommendations:** intersects a student's skill set with each job's
  required skills to compute `match %`, `matched_skills`, and
  `missing_skills` (`agents/recommendation_agent.py`).

## Notes for the demo

- The job dataset is static/seeded — no external API calls, so it works
  fully offline.
- CORS is open (`allow_origins=["*"]`) to keep the frontend-backend handoff
  frictionless during the hackathon; tighten this before any real deployment.
- This was built and validated in a sandboxed environment without outbound
  network access, so the agent logic (skill extraction, domain prediction,
  plagiarism scoring, job matching) was unit-tested directly, but the live
  `uvicorn` server itself wasn't run end-to-end. Do a quick smoke test after
  `pip install -r requirements.txt` before your demo.
