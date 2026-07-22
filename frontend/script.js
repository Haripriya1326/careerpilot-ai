/* =========================================================================
   CareerPilot AI — script.js
   Vanilla JS controller shared across dashboard.html and profile.html.
   Talks to the FastAPI backend at API_BASE_URL using the Fetch API and
   keeps a tiny bit of session state (pilot name + last student id) in
   localStorage so the flow survives page navigation.
   ========================================================================= */

const API_BASE_URL = "http://localhost:8000";

/* ---------- Small shared helpers ---------- */

function getStoredStudentId() {
  const value = localStorage.getItem("cp_student_id");
  return value ? Number(value) : null;
}

function setStoredStudentId(id) {
  localStorage.setItem("cp_student_id", id);
}

function matchTierClass(matchPercent) {
  if (matchPercent >= 70) return "cp-match-high";
  if (matchPercent >= 40) return "cp-match-mid";
  return "cp-match-low";
}

function buildChip(label, variant, delayIndex) {
  const chip = document.createElement("span");
  chip.className = variant ? `cp-chip ${variant}` : "cp-chip";
  chip.textContent = label;
  if (typeof delayIndex === "number") {
    chip.style.animationDelay = `${Math.min(delayIndex * 0.04, 0.3)}s`;
  }
  return chip;
}

/* ---------- Dashboard: greeting ---------- */

function renderPilotGreeting() {
  const nameEl = document.getElementById("cp-pilot-name");
  if (!nameEl) return;
  const storedName = localStorage.getItem("cp_pilot_name");
  nameEl.textContent = storedName || "Pilot";
}

/* ---------- Dashboard: upload flow ---------- */

function initUploadZone() {
  const dropZone = document.getElementById("cp-drop-zone");
  const fileInput = document.getElementById("cp-resume-input");
  const filenameDisplay = document.getElementById("cp-filename-display");
  if (!dropZone || !fileInput) return;

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      filenameDisplay.textContent = fileInput.files[0].name;
    }
  });

  ["dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      if (eventName === "dragover") dropZone.classList.add("cp-drag");
      if (eventName === "dragleave" || eventName === "drop") dropZone.classList.remove("cp-drag");
    });
  });

  dropZone.addEventListener("drop", (event) => {
    const droppedFiles = event.dataTransfer.files;
    if (droppedFiles.length > 0) {
      fileInput.files = droppedFiles;
      filenameDisplay.textContent = droppedFiles[0].name;
    }
  });
}

function showUploadStatus(message, isError) {
  const statusEl = document.getElementById("cp-upload-status");
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.className = `cp-status cp-status-show ${isError ? "cp-status-warn" : "cp-status-ok"}`;
}

async function handleResumeUpload(event) {
  event.preventDefault();

  const fileInput = document.getElementById("cp-resume-input");
  const uploadBtn = document.getElementById("cp-upload-btn");
  const file = fileInput.files[0];

  if (!file) {
    showUploadStatus("Please choose a PDF resume first.", true);
    return;
  }

  const pilotName = localStorage.getItem("cp_pilot_name") || "Anonymous Pilot";
  const pilotEmail = localStorage.getItem("cp_pilot_email") || "";

  const formData = new FormData();
  formData.append("name", pilotName);
  formData.append("email", pilotEmail);
  formData.append("resume", file);

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Scanning…";

  try {
    const response = await fetch(`${API_BASE_URL}/upload-resume`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "Upload failed.");
    }

    const result = await response.json();
    setStoredStudentId(result.student_id);

    showUploadStatus("Resume scanned successfully.", false);
    renderScanResults(result);
    loadRecommendations(result.student_id);
  } catch (error) {
    showUploadStatus(error.message || "Something went wrong during upload.", true);
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Run resume scan";
  }
}

function renderScanResults(result) {
  const panel = document.getElementById("cp-results-panel");
  if (!panel) return;
  panel.style.display = "block";

  document.getElementById("cp-domain-value").textContent = result.domain || "Unclassified";
  document.getElementById("cp-skill-count").textContent = result.skills.length;

  const skillsRow = document.getElementById("cp-extracted-skills");
  skillsRow.innerHTML = "";
  if (result.skills.length === 0) {
    skillsRow.appendChild(buildChip("No recognizable skills found"));
  } else {
    result.skills.forEach((skill, i) => skillsRow.appendChild(buildChip(skill, null, i)));
  }

  renderGauge(result.plagiarism_score, result.is_duplicate);
}

function renderGauge(score, isDuplicate) {
  const gauge = document.getElementById("cp-gauge");
  const gaugeText = document.getElementById("cp-gauge-text");
  const caption = document.getElementById("cp-gauge-caption");

  const roundedScore = Math.round(score);
  gauge.style.setProperty("--cp-gauge-pct", roundedScore);
  gauge.style.setProperty("--cp-gauge-color", isDuplicate ? "var(--cp-red)" : "var(--cp-cyan)");
  gaugeText.textContent = `${roundedScore}%`;

  caption.innerHTML = isDuplicate
    ? `<strong>Flagged as a likely duplicate.</strong> This resume closely matches one already on file (${roundedScore}% similarity).`
    : `<strong>Looks original.</strong> Highest similarity against resumes on file is ${roundedScore}%.`;
}

/* ---------- Dashboard: job recommendations ---------- */

async function loadRecommendations(studentId) {
  const container = document.getElementById("cp-jobs-container");
  if (!container) return;

  container.innerHTML = `<div class="cp-empty">Calculating best-fit roles…</div>`;

  try {
    const response = await fetch(`${API_BASE_URL}/recommendations/${studentId}`);
    if (!response.ok) throw new Error("Could not load recommendations.");

    const jobs = await response.json();
    renderJobCards(jobs, container);
  } catch (error) {
    container.innerHTML = `<div class="cp-empty">${error.message}</div>`;
  }
}

function renderJobCards(jobs, container) {
  container.innerHTML = "";

  if (jobs.length === 0) {
    container.innerHTML = `<div class="cp-empty">No matching roles found yet.</div>`;
    return;
  }

  const grid = document.createElement("div");
  grid.className = "cp-job-grid";

  jobs.forEach((job, index) => {
    const card = document.createElement("article");
    card.className = "cp-job-card";
    card.style.animationDelay = `${Math.min(index * 0.06, 0.4)}s`;

    const top = document.createElement("div");
    top.className = "cp-job-card-top";

    const titleBlock = document.createElement("div");
    const roleEl = document.createElement("div");
    roleEl.className = "cp-job-role";
    roleEl.textContent = job.role;
    const companyEl = document.createElement("div");
    companyEl.className = "cp-job-company";
    companyEl.textContent = job.company;
    titleBlock.appendChild(roleEl);
    titleBlock.appendChild(companyEl);

    const badge = document.createElement("span");
    badge.className = `cp-match-badge ${matchTierClass(job.match)}`;
    badge.textContent = `${job.match}% match`;

    top.appendChild(titleBlock);
    top.appendChild(badge);

    const meta = document.createElement("div");
    meta.className = "cp-job-meta";
    meta.textContent = [job.location, job.salary].filter(Boolean).join(" · ");

    const matchedLabel = document.createElement("div");
    matchedLabel.className = "cp-job-skills-label";
    matchedLabel.textContent = "Matched skills";
    const matchedRow = document.createElement("div");
    matchedRow.className = "cp-chip-row";
    if (job.matched_skills.length === 0) {
      matchedRow.appendChild(buildChip("None yet"));
    } else {
      job.matched_skills.forEach((skill, i) => matchedRow.appendChild(buildChip(skill, "cp-chip-matched", i)));
    }

    const missingLabel = document.createElement("div");
    missingLabel.className = "cp-job-skills-label";
    missingLabel.textContent = "Skills to build";
    const missingRow = document.createElement("div");
    missingRow.className = "cp-chip-row";
    if (job.missing_skills.length === 0) {
      missingRow.appendChild(buildChip("Fully matched!", "cp-chip-matched"));
    } else {
      job.missing_skills.forEach((skill, i) => missingRow.appendChild(buildChip(skill, "cp-chip-missing", i)));
    }

    card.appendChild(top);
    card.appendChild(meta);
    card.appendChild(matchedLabel);
    card.appendChild(matchedRow);
    card.appendChild(missingLabel);
    card.appendChild(missingRow);

    grid.appendChild(card);
  });

  container.appendChild(grid);
}

/* ---------- Profile page ---------- */

async function loadProfile() {
  const emptyState = document.getElementById("cp-profile-empty");
  const content = document.getElementById("cp-profile-content");
  if (!emptyState || !content) return;

  const studentId = getStoredStudentId();
  if (!studentId) {
    emptyState.style.display = "block";
    content.style.display = "none";
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/profile/${studentId}`);
    if (!response.ok) throw new Error("Profile not found.");

    const profile = await response.json();

    emptyState.style.display = "none";
    content.style.display = "block";

    document.getElementById("cp-profile-name").textContent = profile.name;
    document.getElementById("cp-profile-email").textContent = profile.email || "—";
    document.getElementById("cp-profile-domain").textContent = profile.domain || "Unclassified";

    const skillsRow = document.getElementById("cp-profile-skills");
    skillsRow.innerHTML = "";
    if (profile.skills.length === 0) {
      skillsRow.appendChild(buildChip("No skills on file"));
    } else {
      profile.skills.forEach((skill) => skillsRow.appendChild(buildChip(skill)));
    }

    const plagiarismEl = document.getElementById("cp-profile-plagiarism");
    plagiarismEl.className = `cp-status cp-status-show ${profile.is_duplicate ? "cp-status-warn" : "cp-status-ok"}`;
    plagiarismEl.textContent = profile.is_duplicate
      ? `Flagged as a likely duplicate (${profile.plagiarism_score}% similarity).`
      : `Resume looks original (highest similarity: ${profile.plagiarism_score}%).`;
  } catch (error) {
    emptyState.style.display = "block";
    emptyState.textContent = error.message;
    content.style.display = "none";
  }
}

/* ---------- Page bootstrapping ---------- */

document.addEventListener("DOMContentLoaded", () => {
  renderPilotGreeting();
  initUploadZone();

  const uploadForm = document.getElementById("cp-upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", handleResumeUpload);

    // If a previous scan already happened this session, restore the job list.
    const existingStudentId = getStoredStudentId();
    if (existingStudentId) {
      loadRecommendations(existingStudentId);
    }
  }

  if (document.getElementById("cp-profile-panel")) {
    loadProfile();
  }
});
