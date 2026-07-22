from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.database import get_connection

router = APIRouter()


class LoginUser(BaseModel):
    email: str
    password: str


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

    existing = cursor.fetchone()

    conn.close()

    if existing is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "id": existing["id"],
        "name": existing["name"],
        "email": existing["email"]
    }