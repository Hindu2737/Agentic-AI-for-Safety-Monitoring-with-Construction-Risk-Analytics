import hashlib
import hmac
import os
import re
import secrets
import sqlite3

from datetime import datetime, timedelta

import streamlit as st

from utils.database import (
    get_connection,
    initialize_database,
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_users_table():
    """
    Make sure the application database and users table exist.
    """
    initialize_database()


# ============================================================
# PASSWORD SECURITY
# ============================================================

PBKDF2_ITERATIONS = 310_000


def hash_password(password):
    """
    Hash password using PBKDF2-HMAC-SHA256.
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
    Verify password against stored PBKDF2 hash.
    """
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):
        return False


# Backward-compatible function
def verify_password(password, stored_hash):
    return verify_password_hash(
        password,
        stored_hash,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_email(email):
    """
    Validate email address.
    """
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(
            pattern,
            email,
        )
    )


def validate_username(username):
    """
    Username:
        3-30 characters
        letters
        numbers
        underscore
    """
    pattern = r"^[A-Za-z0-9_]{3,30}$"

    return bool(
        re.match(
            pattern,
            username,
        )
    )


def validate_password(password):
    """
    Password requirements:
        - minimum 8 characters
        - uppercase
        - lowercase
        - number
    """

    if len(password) < 8:
        return (
            False,
            "Password must contain at least 8 characters.",
        )

    if not re.search(r"[A-Z]", password):
        return (
            False,
            "Password must contain at least one uppercase letter.",
        )

    if not re.search(r"[a-z]", password):
        return (
            False,
            "Password must contain at least one lowercase letter.",
        )

    if not re.search(r"[0-9]", password):
        return (
            False,
            "Password must contain at least one number.",
        )

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

    Public signup:
        Worker only.

    Admin-created accounts:
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

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not full_name:
        return False, "Full name is required."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if not validate_username(username):
        return (
            False,
            "Username must contain 3-30 characters "
            "using only letters, numbers or underscore.",
        )

    password_valid, password_message = validate_password(
        password
    )

    if not password_valid:
        return False, password_message

    if role not in allowed_roles:
        return False, "Invalid user role."

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

        # Check email
        existing_email = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
            LIMIT 1
            """,
            (email,),
        ).fetchone()

        if existing_email:
            return (
                False,
                "An account with this email already exists.",
            )

        # Check username
        existing_username = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(username) = LOWER(?)
            LIMIT 1
            """,
            (username,),
        ).fetchone()

        if existing_username:
            return (
                False,
                "This username is already taken.",
            )

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
            VALUES (
                ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP
            )
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

        return (
            True,
            "Account created successfully.",
        )

    except Exception as e:
        connection.rollback()

        return (
            False,
            f"Unable to create account: {e}",
        )

    finally:
        connection.close()


# ============================================================
# LAST LOGIN
# ============================================================

def update_last_login(user_id):
    """
    Update user's last login timestamp.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user_id,),
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# PERSISTENT LOGIN SESSIONS
# ============================================================

SESSION_DURATION_DAYS = 30


def create_sessions_table():
    """
    Create persistent login sessions table.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_sessions_user
            ON sessions(user_id)
            """
        )

        connection.commit()

    finally:
        connection.close()


def create_login_session(user_id):
    """
    Create a persistent login token.

    Existing sessions for this user are removed.
    """

    create_sessions_table()

    token = secrets.token_urlsafe(48)

    created_at = datetime.now()

    expires_at = (
        created_at
        + timedelta(
            days=SESSION_DURATION_DAYS
        )
    )

    connection = get_connection()

    try:
        # Remove old sessions for this user
        connection.execute(
            """
            DELETE FROM sessions
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.execute(
            """
            INSERT INTO sessions (
                token,
                user_id,
                created_at,
                expires_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                token,
                user_id,
                created_at.isoformat(),
                expires_at.isoformat(),
            ),
        )

        connection.commit()

        return token

    finally:
        connection.close()


def restore_login_session(token):
    """
    Restore Streamlit login from persistent token.

    Returns:
        True  -> restored
        False -> invalid/expired/inactive
    """

    if not token:
        return False

    create_sessions_table()

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

        session = connection.execute(
            """
            SELECT
                s.token,
                s.user_id,
                s.expires_at,

                u.id,
                u.full_name,
                u.email,
                u.username,
                u.role,
                u.is_verified

            FROM sessions s

            INNER JOIN users u
                ON u.id = s.user_id

            WHERE s.token = ?

            LIMIT 1
            """,
            (token,),
        ).fetchone()

        # ----------------------------------------------------
        # Invalid token
        # ----------------------------------------------------

        if not session:
            return False

        # ----------------------------------------------------
        # Check expiry
        # ----------------------------------------------------

        try:
            expires_at = datetime.fromisoformat(
                session["expires_at"]
            )

        except (
            ValueError,
            TypeError,
        ):
            connection.execute(
                """
                DELETE FROM sessions
                WHERE token = ?
                """,
                (token,),
            )

            connection.commit()

            return False

        if datetime.now() > expires_at:

            connection.execute(
                """
                DELETE FROM sessions
                WHERE token = ?
                """,
                (token,),
            )

            connection.commit()

            return False

        # ----------------------------------------------------
        # Check account status
        # ----------------------------------------------------

        if int(session["is_verified"]) == 0:

            connection.execute(
                """
                DELETE FROM sessions
                WHERE token = ?
                """,
                (token,),
            )

            connection.commit()

            return False

        # ----------------------------------------------------
        # Restore Streamlit session
        # ----------------------------------------------------

        st.session_state["authenticated"] = True

        st.session_state["user_id"] = (
            session["id"]
        )

        st.session_state["full_name"] = (
            session["full_name"]
        )

        st.session_state["email"] = (
            session["email"]
        )

        st.session_state["username"] = (
            session["username"]
        )

        st.session_state["user_role"] = (
            session["role"]
        )

        st.session_state["session_token"] = token

        return True

    finally:
        connection.close()


def delete_login_session(token):
    """
    Delete a persistent login session.
    """

    if not token:
        return

    create_sessions_table()

    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM sessions
            WHERE token = ?
            """,
            (token,),
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate_user(identifier, password):
    """
    Authenticate using username OR email.

    Returns:
        user dictionary
        "inactive"
        None
    """

    initialize_users_table()

    identifier = identifier.strip()

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

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
            (
                identifier,
                identifier,
            ),
        ).fetchone()

        # ----------------------------------------------------
        # User doesn't exist
        # ----------------------------------------------------

        if not user:
            return None

        # ----------------------------------------------------
        # Account inactive
        # ----------------------------------------------------

        if int(user["is_verified"]) == 0:
            return "inactive"

        # ----------------------------------------------------
        # Password
        # ----------------------------------------------------

        if not verify_password_hash(
            password,
            user["password_hash"],
        ):
            return None

        # ----------------------------------------------------
        # Last login
        # ----------------------------------------------------

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
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "construction_ai.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Securely hash a password using PBKDF2.
    """

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(password, stored_hash):
    """
    Verify a password against the stored PBKDF2 hash.
    """

    try:
        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100_000,
        )

        return secrets.compare_digest(
            actual_hash,
            expected_hash,
        )

    except Exception:
        return False


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_users_table():
    """
    Create authentication tables if they do not exist.
    """

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL UNIQUE,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            full_name TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'Worker',

            is_verified INTEGER NOT NULL DEFAULT 1,

            created_at TEXT NOT NULL,

            last_login TEXT
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS login_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_token TEXT NOT NULL UNIQUE,

            user_id INTEGER NOT NULL,

            created_at TEXT NOT NULL,

            expires_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def validate_password(password):
    """
    Password requirements:

    - Minimum 8 characters
    - One uppercase letter
    - One lowercase letter
    - One number
    """

    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."

    return True, "Valid password."


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    full_name,
    username,
    email,
    password,
    role="Worker",
):
    """
    Create a new user.

    Returns:
        (True, user_data)
        (False, error_message)
    """

    full_name = full_name.strip()
    username = username.strip()
    email = email.strip().lower()

    if not full_name:
        return False, "Full name is required."

    if not username:
        return False, "Username is required."

    if not email:
        return False, "Email is required."

    password_valid, password_message = validate_password(
        password
    )

    if not password_valid:
        return False, password_message

    allowed_roles = {
        "Admin",
        "Manager",
        "Safety Officer",
        "Worker",
    }

    if role not in allowed_roles:
        role = "Worker"

    connection = get_connection()

    try:

        existing_username = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(username) = LOWER(?)
            """,
            (username,),
        ).fetchone()

        if existing_username:
            return False, "Username already exists."

        existing_email = connection.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
            """,
            (email,),
        ).fetchone()

        if existing_email:
            return False, "Email already exists."

        password_hash = hash_password(
            password
        )

        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        cursor = connection.execute(
            """
            INSERT INTO users (
                username,
                email,
                password_hash,
                full_name,
                role,
                is_verified,
                created_at,
                last_login
            )
            VALUES (?, ?, ?, ?, ?, 1, ?, NULL)
            """,
            (
                username,
                email,
                password_hash,
                full_name,
                role,
                created_at,
            ),
        )

        connection.commit()

        user_id = cursor.lastrowid

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        return True, dict(user)

    except sqlite3.IntegrityError as error:

        connection.rollback()

        return False, str(error)

    finally:

        connection.close()


# ============================================================
# LOGIN
# ============================================================

def login_user(identifier, password):
    """
    Authenticate a user.

    Returns:

        (True, user_data)
            Login successful.

        (False, "inactive")
            Account has been deactivated.

        (False, "invalid")
            Invalid username/email/password.
    """

    identifier = identifier.strip()

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(username) = LOWER(?)
           OR LOWER(email) = LOWER(?)
        LIMIT 1
        """,
        (
            identifier,
            identifier,
        ),
    ).fetchone()

    if not user:

        connection.close()

        return False, "invalid"

    # --------------------------------------------------------
    # IMPORTANT:
    # Check inactive account BEFORE password verification.
    # --------------------------------------------------------

    if int(user["is_verified"]) == 0:

        connection.close()

        return False, "inactive"

    if not verify_password(
        password,
        user["password_hash"],
    ):

        connection.close()

        return False, "invalid"

    # --------------------------------------------------------
    # Update last login
    # --------------------------------------------------------

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    connection.execute(
        """
        UPDATE users
        SET last_login = ?
        WHERE id = ?
        """,
        (
            now,
            user["id"],
        ),
    )

    connection.commit()

    connection.close()

    return True, dict(user)


# ============================================================
# CREATE LOGIN SESSION
# ============================================================

def create_login_session(user_id):
    """
    Create a persistent login token.

    The token is stored in the database so the login
    can survive Streamlit page refreshes.
    """

    initialize_users_table()

    connection = get_connection()

    # Remove old sessions belonging to this user.
    connection.execute(
        """
        DELETE FROM login_sessions
        WHERE user_id = ?
        """,
        (user_id,),
    )

    session_token = secrets.token_urlsafe(48)

    created_at = datetime.now()

    expires_at = (
        created_at
        + timedelta(days=7)
    )

    connection.execute(
        """
        INSERT INTO login_sessions (
            session_token,
            user_id,
            created_at,
            expires_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session_token,
            user_id,
            created_at.isoformat(
                timespec="seconds"
            ),
            expires_at.isoformat(
                timespec="seconds"
            ),
        ),
    )

    connection.commit()

    connection.close()

    return session_token


# ============================================================
# RESTORE LOGIN SESSION
# ============================================================

def restore_login_session(session_token):
    """
    Restore a user's authentication state from
    the URL session token.

    Returns:
        True  -> restored
        False -> invalid/expired session
    """

    if not session_token:
        return False

    initialize_users_table()

    connection = get_connection()

    session = connection.execute(
        """
        SELECT
            login_sessions.*,
            users.username,
            users.email,
            users.full_name,
            users.role,
            users.is_verified
        FROM login_sessions
        INNER JOIN users
            ON users.id = login_sessions.user_id
        WHERE login_sessions.session_token = ?
        LIMIT 1
        """,
        (session_token,),
    ).fetchone()

    if not session:

        connection.close()

        return False

    # --------------------------------------------------------
    # Check expiration
    # --------------------------------------------------------

    try:

        expires_at = datetime.fromisoformat(
            session["expires_at"]
        )

        if datetime.now() > expires_at:

            connection.execute(
                """
                DELETE FROM login_sessions
                WHERE session_token = ?
                """,
                (session_token,),
            )

            connection.commit()

            connection.close()

            return False

    except Exception:

        connection.close()

        return False

    # --------------------------------------------------------
    # Check account status
    # --------------------------------------------------------

    if int(session["is_verified"]) == 0:

        connection.close()

        return False

    connection.close()

    # --------------------------------------------------------
    # Restore Streamlit session
    # --------------------------------------------------------

    import streamlit as st

    st.session_state["authenticated"] = True

    st.session_state["user_id"] = session["user_id"]

    st.session_state["full_name"] = session["full_name"]

    st.session_state["email"] = session["email"]

    st.session_state["username"] = session["username"]

    st.session_state["user_role"] = session["role"]

    st.session_state["session_token"] = session_token

    return True


# ============================================================
# LOGOUT
# ============================================================

def logout_user(session_token=None):
    """
    Completely log the user out.
    """

    import streamlit as st

    if session_token is None:
        session_token = st.session_state.get(
            "session_token"
        )

    if session_token:

        connection = get_connection()

        connection.execute(
            """
            DELETE FROM login_sessions
            WHERE session_token = ?
            """,
            (session_token,),
        )

        connection.commit()

        connection.close()

    # --------------------------------------------------------
    # Clear authentication state
    # --------------------------------------------------------

    keys_to_remove = [
        "authenticated",
        "user_id",
        "full_name",
        "email",
        "username",
        "user_role",
        "session_token",
    ]

    for key in keys_to_remove:

        st.session_state.pop(
            key,
            None,
        )


# ============================================================
# UPDATE LAST LOGIN
# ============================================================

def update_last_login(user_id):

    connection = get_connection()

    connection.execute(
        """
        UPDATE users
        SET last_login = ?
        WHERE id = ?
        """,
        (
            datetime.now().isoformat(
                timespec="seconds"
            ),
            user_id,
        ),
    )

    connection.commit()

    connection.close()


# ============================================================
# ACTIVATE USER
# ============================================================

def activate_user(user_id):

    connection = get_connection()

    connection.execute(
        """
        UPDATE users
        SET is_verified = 1
        WHERE id = ?
        """,
        (user_id,),
    )

    connection.commit()

    connection.close()

    return True


# ============================================================
# DEACTIVATE USER
# ============================================================

def deactivate_user(user_id):

    connection = get_connection()

    # Disable account
    connection.execute(
        """
        UPDATE users
        SET is_verified = 0
        WHERE id = ?
        """,
        (user_id,),
    )

    # Remove existing sessions
    connection.execute(
        """
        DELETE FROM login_sessions
        WHERE user_id = ?
        """,
        (user_id,),
    )

    connection.commit()

    connection.close()

    return True


# ============================================================
# GET ALL USERS
# ============================================================

def get_all_users():

    connection = get_connection()

    users = connection.execute(
        """
        SELECT *
        FROM users
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return [dict(user) for user in users]


# ============================================================
# GET USER
# ============================================================

def get_user_by_id(user_id):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()

    connection.close()

    if not user:
        return None

    return dict(user)


# ============================================================
# UPDATE USER ROLE
# ============================================================

def update_user_role(user_id, role):

    allowed_roles = {
        "Admin",
        "Manager",
        "Safety Officer",
        "Worker",
    }

    if role not in allowed_roles:
        return False

    connection = get_connection()

    connection.execute(
        """
        UPDATE users
        SET role = ?
        WHERE id = ?
        """,
        (
            role,
            user_id,
        ),
    )

    connection.commit()

    connection.close()

    return True


# ============================================================
# DELETE USER
# ============================================================

def delete_user(user_id):

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM login_sessions
        WHERE user_id = ?
        """,
        (user_id,),
    )

    connection.execute(
        """
        DELETE FROM users
        WHERE id = ?
        """,
        (user_id,),
    )

    connection.commit()

    connection.close()

    return True


# ============================================================
# INITIALIZE DATABASE ON IMPORT
# ============================================================

initialize_users_table()

# ============================================================
# LOGIN USER
# ============================================================

def login_user(identifier, password):
    """
    Login user.

    Returns:
        (True, user_data)
        (False, "inactive")
        (False, "invalid")
    """

    user = authenticate_user(
        identifier,
        password,
    )

    # --------------------------------------------------------
    # Inactive
    # --------------------------------------------------------

    if user == "inactive":
        return False, "inactive"

    # --------------------------------------------------------
    # Invalid
    # --------------------------------------------------------

    if not user:
        return False, "invalid"

    # --------------------------------------------------------
    # Store Streamlit session
    # --------------------------------------------------------

    st.session_state["authenticated"] = True

    st.session_state["user_id"] = user["id"]

    st.session_state["full_name"] = (
        user["full_name"]
    )

    st.session_state["email"] = (
        user["email"]
    )

    st.session_state["username"] = (
        user["username"]
    )

    st.session_state["user_role"] = (
        user["role"]
    )

    # --------------------------------------------------------
    # Create persistent session
    # --------------------------------------------------------

    token = create_login_session(
        user["id"]
    )

    st.session_state["session_token"] = token

    # Keep token in browser URL
    st.query_params["session"] = token

    return True, user


# ============================================================
# LOGOUT
# ============================================================

def logout_user():
    """
    Completely log the current user out.
    """

    token = st.session_state.get(
        "session_token"
    )

    if token:
        delete_login_session(token)

    keys_to_remove = [
        "authenticated",
        "user_id",
        "full_name",
        "email",
        "username",
        "user_role",
        "session_token",
        "analysis_result",
        "dashboard_analysis_result",
        "last_saved_inspection_id",
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None,
        )

    try:
        st.query_params.clear()
    except Exception:
        pass


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
    current_role = st.session_state.get(
        "user_role"
    )

    return current_role in roles


# ============================================================
# GET ALL USERS
# ============================================================

def get_all_users():
    """
    Return all users for Admin Portal.
    """

    initialize_users_table()

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                full_name,
                email,
                username,
                role,
                is_verified,
                created_at,
                last_login

            FROM users

            ORDER BY id DESC
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================
# UPDATE USER ROLE
# ============================================================

def update_user_role(
    user_id,
    new_role,
):
    """
    Change user role.
    """

    allowed_roles = {
        "Admin",
        "Project Manager",
        "Safety Officer",
        "Worker",
    }

    if new_role not in allowed_roles:
        return False, "Invalid role."

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE users
            SET role = ?
            WHERE id = ?
            """,
            (
                new_role,
                user_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return False, "User not found."

        return (
            True,
            "User role updated successfully.",
        )

    finally:
        connection.close()


# ============================================================
# ACTIVATE / DEACTIVATE USER
# ============================================================

def update_user_status(
    user_id,
    is_verified,
):
    """
    Activate or deactivate user.

    is_verified = 1 -> Active
    is_verified = 0 -> Inactive
    """

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # Update status
        # ----------------------------------------------------

        cursor = connection.execute(
            """
            UPDATE users
            SET is_verified = ?
            WHERE id = ?
            """,
            (
                1 if is_verified else 0,
                user_id,
            ),
        )

        # ----------------------------------------------------
        # If deactivated, kill all login sessions
        # ----------------------------------------------------

        if cursor.rowcount > 0 and not is_verified:

            connection.execute(
                """
                DELETE FROM sessions
                WHERE user_id = ?
                """,
                (user_id,),
            )

        connection.commit()

        if cursor.rowcount == 0:
            return (
                False,
                "User not found.",
            )

        if is_verified:
            return (
                True,
                "User activated successfully.",
            )

        return (
            True,
            "User deactivated successfully.",
        )

    finally:
        connection.close()


# ============================================================
# DELETE USER
# ============================================================

def delete_user(user_id):
    """
    Delete user and their sessions.
    """

    connection = get_connection()

    try:

        # Delete sessions first
        connection.execute(
            """
            DELETE FROM sessions
            WHERE user_id = ?
            """,
            (user_id,),
        )

        cursor = connection.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (user_id,),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return (
                False,
                "User not found.",
            )

        return (
            True,
            "User deleted successfully.",
        )

    finally:
        connection.close()


# ============================================================
# USER STATISTICS
# ============================================================

def get_user_statistics():
    """
    Return counts by role.
    """

    initialize_users_table()

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row

        total = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            """
        ).fetchone()["count"]

        admins = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            WHERE role = 'Admin'
            """
        ).fetchone()["count"]

        managers = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            WHERE role = 'Project Manager'
            """
        ).fetchone()["count"]

        safety_officers = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            WHERE role = 'Safety Officer'
            """
        ).fetchone()["count"]

        workers = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            WHERE role = 'Worker'
            """
        ).fetchone()["count"]

        return {
            "total": total,
            "admins": admins,
            "project_managers": managers,
            "safety_officers": safety_officers,
            "workers": workers,
        }

    finally:
        connection.close()