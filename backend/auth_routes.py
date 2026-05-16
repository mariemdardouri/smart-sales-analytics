from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import conn
from auth import hash_password, verify_password, create_token
from datetime import datetime

router = APIRouter()

# ================= MODELS =================

class User(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class UpdateUser(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool


# ================= UTIL DB SAFE =================

def get_cursor():
    # IMPORTANT: nouveau cursor propre à chaque requête
    return conn.cursor()


# ================= SIGNUP =================

@router.post("/signup")
def signup(user: User):
    cur = get_cursor()

    cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cur.fetchone():
        cur.close()
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)

    cur.execute("""
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """, (user.username, user.email, hashed, "user", True))

    conn.commit()
    cur.close()

    return {"message": "User created successfully"}


# ================= LOGIN =================

@router.post("/login")
def login(user: Login):
    cur = get_cursor()

    cur.execute("""
        SELECT id, username, password_hash, role, is_active
        FROM users
        WHERE email=%s
    """, (user.email,))

    db_user = cur.fetchone()

    if not db_user:
        cur.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_id, username, hashed, role, is_active = db_user

    if not is_active:
        cur.close()
        raise HTTPException(status_code=403, detail="Account disabled")

    if not verify_password(user.password, hashed):
        cur.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")

    cur.execute("""
        UPDATE users SET last_login=%s WHERE id=%s
    """, (datetime.now(), user_id))

    conn.commit()
    cur.close()

    token = create_token({
        "user_id": user_id,
        "role": role
    })

    return {
        "access_token": token,
        "role": role,
        "username": username
    }


# ================= GET USERS =================

@router.get("/admin/users")
def get_users():
    cur = get_cursor()

    try:
        cur.execute("""
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users
            ORDER BY id DESC
        """)

        users = cur.fetchall()

        result = []
        for u in users:
            result.append({
                "id": u[0],
                "username": u[1],
                "email": u[2],
                "role": u[3],
                "is_active": u[4],
                "created_at": str(u[5]) if u[5] else None,
                "last_login": str(u[6]) if u[6] else "Never"
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()


# ================= UPDATE USER =================

@router.put("/admin/users/{user_id}")
def update_user(user_id: int, data: UpdateUser):
    cur = get_cursor()

    cur.execute("""
        UPDATE users
        SET username=%s,
            email=%s,
            role=%s,
            is_active=%s
        WHERE id=%s
    """, (
        data.username,
        data.email,
        data.role,
        data.is_active,
        user_id
    ))

    conn.commit()
    cur.close()

    return {"message": "User updated successfully"}


# ================= TOGGLE ACTIVE =================

@router.put("/admin/users/toggle/{user_id}")
def toggle_user(user_id: int):
    cur = get_cursor()

    cur.execute("SELECT is_active FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.close()
        raise HTTPException(status_code=404, detail="User not found")

    new_status = not user[0]

    cur.execute("""
        UPDATE users SET is_active=%s WHERE id=%s
    """, (new_status, user_id))

    conn.commit()
    cur.close()

    return {
        "message": "Status updated",
        "is_active": new_status
    }


# ================= STATS =================

@router.get("/admin/stats")
def user_stats():
    cur = get_cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL
    """)
    logged_users = cur.fetchone()[0]

    cur.execute("""
        SELECT DATE_TRUNC('month', created_at), COUNT(*)
        FROM users
        GROUP BY 1
        ORDER BY 1
    """)

    monthly = cur.fetchall()
    cur.close()

    return {
        "total_users": total_users,
        "logged_users": logged_users,
        "monthly_users": [
            {"month": str(m[0])[:7], "count": m[1]}
            for m in monthly
        ]
    }