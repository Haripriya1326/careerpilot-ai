from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.database import get_connection

router = APIRouter()


# ==========================
# REGISTER MODEL
# ==========================
class RegisterUser(BaseModel):
    name: str
    email: str
    password: str


# ==========================
# LOGIN MODEL
# ==========================
class LoginUser(BaseModel):
    email: str
    password: str


# ==========================
# REGISTER API
# ==========================
@router.post("/register")
def register(user: RegisterUser):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (user.email,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    cursor.execute(
        """
        INSERT INTO users(name, email, password)
        VALUES (?, ?, ?)
        """,
        (
            user.name,
            user.email,
            user.password
        )
    )

    conn.commit()
    conn.close()

    return {
        "message": "Account created successfully"
    }


# ==========================
# LOGIN API
# ==========================
@router.post("/login")
def login(user: LoginUser):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email=? AND password=?
        """,
        (
            user.email,
            user.password
        )
    )

    logged_user = cursor.fetchone()

    conn.close()

    if not logged_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "id": logged_user["id"],
        "name": logged_user["name"],
        "email": logged_user["email"],
        "message": "Login successful"
    }