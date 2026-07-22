const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("cp-login-form");
    const signupForm = document.getElementById("signup-form");

    const signupModal = document.getElementById("signup-modal");
    const createBtn = document.getElementById("create-account-btn");
    const closeBtn = document.getElementById("close-signup");

    const loginMessage = document.getElementById("login-message");

    /* ===========================
       OPEN SIGNUP POPUP
    =========================== */

    createBtn.addEventListener("click", () => {
        signupModal.style.display = "flex";
    });

    /* ===========================
       CLOSE SIGNUP POPUP
    =========================== */

    closeBtn.addEventListener("click", () => {
        signupModal.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === signupModal) {
            signupModal.style.display = "none";
        }
    });

    /* ===========================
       REGISTER
    =========================== */

    signupForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const name = document.getElementById("signup-name").value.trim();
        const email = document.getElementById("signup-email").value.trim();
        const password = document.getElementById("signup-password").value.trim();

        try {

            const response = await fetch(`${API_BASE_URL}/register`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name,
                    email,
                    password
                })

            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail);
                return;
            }

            alert("Account created successfully!");

            signupForm.reset();

            signupModal.style.display = "none";

        }
        catch (err) {

            alert("Cannot connect to backend.");

        }

    });

    /* ===========================
       LOGIN
    =========================== */

    loginForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value.trim();

        try {

            const response = await fetch(`${API_BASE_URL}/login`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email,
                    password
                })

            });

            const data = await response.json();

            if (!response.ok) {

                loginMessage.className =
                    "cp-status cp-status-show cp-status-warn";

                loginMessage.textContent =
                    data.detail;

                return;

            }

            localStorage.setItem("cp_pilot_name", data.name);
            localStorage.setItem("cp_pilot_email", data.email);
            localStorage.setItem("cp_user_id", data.id);

            window.location.href = "dashboard.html";

        }
        catch (err) {

            loginMessage.className =
                "cp-status cp-status-show cp-status-warn";

            loginMessage.textContent =
                "Cannot connect to backend.";

        }

    });

});