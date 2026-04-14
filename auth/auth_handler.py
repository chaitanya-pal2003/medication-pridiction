"""
auth/auth_handler.py
Password hashing, registration, login, and session helpers.
"""
import bcrypt
import streamlit as st
from db_connector import execute_query
from auth.cookie_manager import set_auth_cookie, delete_auth_cookie
import time


# ─── Password helpers ─────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ─── Register ─────────────────────────────────────────────────────────────────
def register_user(name: str, email: str, password: str) -> dict:
    """Register a new user. Returns {'success': bool, ...}"""
    existing = execute_query(
        "SELECT id FROM users WHERE email = %s", (email,), fetch=True
    )
    if existing:
        return {"success": False, "message": "An account with that email already exists."}

    pw_hash = hash_password(password)
    user_id = execute_query(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name.strip(), email.strip().lower(), pw_hash),
    )
    return {
        "success":  True,
        "user_id":  user_id,
        "name":     name.strip(),
        "email":    email.strip().lower(),
    }


# ─── Login ────────────────────────────────────────────────────────────────────
def login_user(email: str, password: str) -> dict:
    """Validate credentials and check account status."""
    rows = execute_query(
        "SELECT * FROM users WHERE email = %s", (email.strip().lower(),), fetch=True
    )
    if not rows:
        return {"success": False, "message": "No account found with that email address."}

    user = rows[0]

    # Check if user is suspended
    if user.get("status") == "suspended":
        return {"success": False, "message": "Your account has been suspended by an Administrator."}

    if verify_password(password, user["password_hash"]):
        return {
            "success": True,
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user")  # Default to user if upgrading old DB
        }
    return {"success": False, "message": "Incorrect password. Please try again."}




# ─── Session helpers ──────────────────────────────────────────────────────────
def set_session(user_data: dict, remember_me: bool = True) -> None:
    """Write user data into Streamlit session state and save cookie."""
    st.session_state["logged_in"]  = True
    st.session_state["user_id"]    = user_data["user_id"]
    st.session_state["user_name"]  = user_data["name"]
    st.session_state["user_email"] = user_data["email"]
    st.session_state["role"]       = user_data.get("role", "user")

    # Save to browser cookies so they survive page refreshes
    if remember_me:
        set_auth_cookie(user_data)

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def logout():
    """Logs the user out by clearing session state and cookies safely."""
    from auth.cookie_manager import delete_auth_cookie

    # 1. Tell the browser to delete the cookie
    delete_auth_cookie()

    # 2. Flag to tell our app to IGNORE any leftover ghost cookies
    st.session_state["just_logged_out"] = True

    # 3. Clear all user session data
    for key in ["user_name", "user_email", "role", "logged_in"]:
        if key in st.session_state:
            del st.session_state[key]

    # 4. Refresh to show the login screen
    st.rerun()

