import hashlib
import hmac
import os
import re

import streamlit as st

from utils.database import get_connection, initialize_database


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_users_table():
    """
    Make sure the users table exists.
    """
    initialize_database()


# ============================================================
# PASSWORD SECURITY
# ============================================================

PBKDF2_ITERATIONS = 310_000


def hash_password(password):
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.
    """
    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return f"{salt.hex()}${password_hash.hex()}"


def verify_password_hash(password, stored_hash):
    """
    Verify a password against the stored PBKDF2 hash.
    """
    try:
        salt_hex, hash_hex = stored_hash.split("$")

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDATION
# ============================================================

def validate_email(email):
    """
    Validate email format.
    """
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def validate_username(username):
    """
    Username:
    - 3 to 30 characters
    - letters, numbers and underscore
    """
    pattern = r"^[A-Za-z0-9_]{3,30}$"
    return bool(re.match(pattern, username))


def validate_password(password):
    """
    Password requirements:
    - minimum 8 characters
    - uppercase
    - lowercase
    - number
    """
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    return True, "Password is valid."


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

    Public signup should use:
        role="Worker"

    Admin-created accounts can use:
        Admin
        Project Manager
        Safety Officer
        Worker
    """

    initialize_users_table()

    full_name = full_name.strip()
    email = email.strip().lower()
    username = username.strip()

    allowed_roles = {
        "Admin",
        "Project Manager",
        "Safety Officer",
        "Worker",
    }

    # -----------------------------
    # Basic validation
    # -----------------------------

    if not full_name:
        return False, "Full name is required."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if not validate_username(username):
        return False, (
            "Username must contain 3-30 characters "
            "using only letters, numbers or underscore."
        )

    password_valid, password_message = validate_password(password)

    if not password_valid:
        return False, password_message

    if role not in allowed_roles:
        return False, "Invalid user role."

    # -----------------------------
    # Check duplicate user
    # -----------------------------

    connection = get_connection()

    try:
        existing_email = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
            """,
            (email,),
        ).fetchone()

        if existing_email:
            return False, "An account with this email already exists."

        existing_username = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(username) = LOWER(?)
            """,
            (username,),
        ).fetchone()

        if existing_username:
            return False, "This username is already taken."

        # -----------------------------
        # Create account
        # -----------------------------

        password_hash = hash_password(password)

        connection.execute(
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
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            """,
            (
                full_name,
                email,
                username,
                password_hash,
                role,
            ),
        )

        connection.commit()

        return True, "Account created successfully."

    except Exception as e:
        return False, f"Unable to create account: {e}"

    finally:
        connection.close()


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(identifier, password):
    """
    Authenticate using username OR email.
    """

    initialize_users_table()

    identifier = identifier.strip()

    connection = get_connection()

    try:
        user = connection.execute(
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
            WHERE LOWER(username) = LOWER(?)
               OR LOWER(email) = LOWER(?)
            LIMIT 1
            """,
            (identifier, identifier),
        ).fetchone()

        if not user:
            return None

        if not user["is_verified"]:
            return None

        if not verify_password_hash(
            password,
            user["password_hash"],
        ):
            return None

        connection.execute(
            """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user["id"],),
        )

        connection.commit()

        return {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        }

    finally:
        connection.close()


# ============================================================
# LOGIN
# ============================================================

def login_user(identifier, password):
    """
    Authenticate and store user information in Streamlit session.
    """

    user = authenticate_user(identifier, password)

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
    """
    Log the current user out.
    """

    keys_to_clear = [
        "authenticated",
        "user_id",
        "full_name",
        "email",
        "username",
        "user_role",
        "analysis_result",
        "dashboard_analysis_result",
        "last_saved_inspection_id",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


# ============================================================
# AUTHENTICATION CHECK
# ============================================================

def is_authenticated():
    return st.session_state.get(
        "authenticated",
        False,
    )


# ============================================================
# ROLE CHECK
# ============================================================

def has_role(*roles):
    """
    Check whether the logged-in user has one of the given roles.
    """

    current_role = st.session_state.get(
        "user_role"
    )

    return current_role in roles