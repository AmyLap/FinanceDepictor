import hashlib
import hmac
import secrets
import sqlite3

import streamlit as st

DB_PATH = "finance.db"


def get_db_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def initialize_auth_db() -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password_hash TEXT,
                password_salt TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        if "password_hash" not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        if "password_salt" not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_salt TEXT")

        conn.commit()


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    if salt_hex is None:
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)

    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt_hex, password_hash.hex()


def create_user(name: str, email: str, password: str) -> tuple[bool, str]:
    clean_name = name.strip()
    clean_email = email.strip().lower()

    if not clean_name:
        return False, "Name is required."
    if not clean_email:
        return False, "Email is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE lower(email) = ?", (clean_email,))
        if cursor.fetchone() is not None:
            return False, "An account with this email already exists."

        salt_hex, password_hash_hex = hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, password_salt)
            VALUES (?, ?, ?, ?)
            """,
            (clean_name, clean_email, password_hash_hex, salt_hex),
        )
        conn.commit()

    return True, "Account created. You can now sign in."


def authenticate_user(email: str, password: str) -> dict | None:
    clean_email = email.strip().lower()
    if not clean_email or not password:
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, email, password_hash, password_salt
            FROM users
            WHERE lower(email) = ?
            """,
            (clean_email,),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    user_id, name, db_email, password_hash_db, password_salt_db = row

    if not password_hash_db or not password_salt_db:
        return None

    _, password_hash_attempt = hash_password(password, password_salt_db)
    if not hmac.compare_digest(password_hash_attempt, password_hash_db):
        return None

    return {"id": user_id, "name": name, "email": db_email}


def ensure_session_keys() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None


def render_auth_page() -> None:
    st.sidebar.title("💰 Finance Depictor")
    auth_page = st.sidebar.radio("Account", ["Login", "Sign Up"])

    st.title("🔐 Finance Depictor")
    st.caption("Sign in to access your dashboard and statement tools.")

    if auth_page == "Login":
        with st.form("login_form"):
            st.subheader("Login")
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")

        if login_submit:
            user = authenticate_user(login_email, login_password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    else:
        with st.form("signup_form"):
            st.subheader("Create Account")
            signup_name = st.text_input("Name")
            signup_email = st.text_input("Email")
            signup_password = st.text_input("Password", type="password")
            signup_password_confirm = st.text_input("Confirm Password", type="password")
            signup_submit = st.form_submit_button("Create Account")

        if signup_submit:
            if signup_password != signup_password_confirm:
                st.error("Passwords do not match.")
            else:
                created, message = create_user(signup_name, signup_email, signup_password)
                if created:
                    st.success(message)
                else:
                    st.error(message)


def guard_authenticated() -> None:
    initialize_auth_db()
    ensure_session_keys()

    if not st.session_state.authenticated:
        render_auth_page()
        st.stop()


def render_user_sidebar() -> None:
    st.sidebar.title("💰 Finance Depictor")
    st.sidebar.caption(f"Signed in as: {st.session_state.user['name']}")
    if st.sidebar.button("Log out"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    st.sidebar.divider()
