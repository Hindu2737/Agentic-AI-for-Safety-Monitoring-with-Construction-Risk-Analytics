import hashlib
import hmac
import re
import secrets
from datetime import datetime

import streamlit as st

from utils.database import get_connection


# ============================================================
# AUTHENTICATION CONFIGURATION
# ============================================================

PASSWORD_ITERATIONS = 310_000


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_users_table():
    """
    Create the users table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Worker',
            is_verified INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.
    """

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    return (
        f"{salt.hex()}$"
        f"{PASSWORD_ITERATIONS}$"
        f"{password_hash.hex()}"
    )


def verify_password_hash(password, stored_hash):
    """
    Verify a password against the stored password hash.
    """

    try:
        salt_hex, iterations, hash_hex = stored_hash.split("$")

        salt = bytes.fromhex(salt_hex)

        iterations = int(iterations)

        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except Exception:
        return False


# ============================================================
# VALIDATION
# ============================================================

def validate_email(email):
    """
    Basic email validation.
    """

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, email) is not None


def validate_username(username):
    """
    Username can contain letters, numbers, underscore and dot.
    """

    pattern = r"^[A-Za-z0-9_.]{3,30}$"

    return re.match(pattern, username) is not None


def validate_password(password):
    """
    Minimum password requirements.
    """

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."

    return True, ""


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    full_name,
    email,
    username,
    password,
    role="Worker",
):
    """
    Create a new user.

    Public signup is expected to use the default Worker role.
    """

    initialize_users_table()

    full_name = full_name.strip()
    email = email.strip().lower()
    username = username.strip()

    if not full_name:
        return False, "Full name is required."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if not validate_username(username):
        return (
            False,
            "Username must contain 3-30 letters, numbers, underscores or dots.",
        )

    valid_password, password_message = validate_password(password)

    if not valid_password:
        return False, password_message

    # Public registration must never create privileged accounts.
    if role not in [
        "Worker",
        "Project Manager",
        "Safety Officer",
        "Admin",
    ]:
        role = "Worker"

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # Check email
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        )

        if cursor.fetchone():
            return False, "An account with this email already exists."

        # Check username
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        )

        if cursor.fetchone():
            return False, "This username is already taken."

        password_hash = hash_password(password)

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                username,
                password_hash,
                role,
                is_verified,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                email,
                username,
                password_hash,
                role,
                1,
                created_at,
            ),
        )

        connection.commit()

        return True, "Account created successfully."

    except Exception as e:

        connection.rollback()

        return False, f"Unable to create account: {e}"

    finally:

        connection.close()


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(identifier, password):
    """
    Authenticate using either username or email.
    """

    initialize_users_table()

    identifier = identifier.strip().lower()

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                username,
                password_hash,
                role,
                is_verified
            FROM users
            WHERE LOWER(username) = ?
               OR LOWER(email) = ?
            LIMIT 1
            """,
            (
                identifier,
                identifier,
            ),
        )

        user = cursor.fetchone()

        if not user:
            return None

        # sqlite3.Row support
        if hasattr(user, "keys"):

            stored_hash = user["password_hash"]

            if not verify_password_hash(
                password,
                stored_hash,
            ):
                return None

            if not user["is_verified"]:
                return None

            cursor.execute(
                """
                UPDATE users
                SET last_login = ?
                WHERE id = ?
                """,
                (
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    user["id"],
                ),
            )

            connection.commit()

            return {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "username": user["username"],
                "role": user["role"],
            }

        # Fallback for tuple-based SQLite connections
        stored_hash = user[4]

        if not verify_password_hash(
            password,
            stored_hash,
        ):
            return None

        if not user[6]:
            return None

        cursor.execute(
            """
            UPDATE users
            SET last_login = ?
            WHERE id = ?
            """,
            (
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                user[0],
            ),
        )

        connection.commit()

        return {
            "id": user[0],
            "full_name": user[1],
            "email": user[2],
            "username": user[3],
            "role": user[5],
        }

    finally:

        connection.close()


# ============================================================
# STREAMLIT LOGIN SESSION
# ============================================================

def login_user(identifier, password):
    """
    Authenticate user and create Streamlit session.
    """

    user = authenticate_user(
        identifier,
        password,
    )

    if not user:
        return False

    st.session_state["authenticated"] = True

    st.session_state["user_id"] = user["id"]

    st.session_state["full_name"] = user["full_name"]

    st.session_state["email"] = user["email"]

    st.session_state["username"] = user["username"]

    st.session_state["user_role"] = user["role"]

    return True


# ============================================================
# LOGOUT
# ============================================================

def logout_user():

    st.session_state["authenticated"] = False

    st.session_state["user_id"] = None

    st.session_state["full_name"] = None

    st.session_state["email"] = None

    st.session_state["username"] = None

    st.session_state["user_role"] = None


# ============================================================
# AUTH STATUS
# ============================================================

def is_authenticated():

    return st.session_state.get(
        "authenticated",
        False,
    )


# ============================================================
# ROLE CHECK
# ============================================================

def has_role(allowed_roles):

    role = st.session_state.get(
        "user_role"
    )

    return role in allowed_roles