import sys
import sqlite3
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ============================================================
# AUTH IMPORTS
# ============================================================

from utils.auth import (
    initialize_users_table,
    create_user,
    login_user,
    logout_user,
    create_login_session,
    restore_login_session,
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "construction_ai.db"
)


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="ConstructAI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# INITIALIZE AUTH DATABASE
# ============================================================

initialize_users_table()


# ============================================================
# SESSION RESTORATION
# ============================================================

def restore_session_from_url():

    if st.session_state.get(
        "authenticated",
        False,
    ):
        return True

    try:

        session_token = st.query_params.get(
            "session"
        )

    except Exception:

        session_token = None

    if not session_token:

        return False

    restored = restore_login_session(
        session_token
    )

    if restored:

        st.session_state[
            "session_token"
        ] = session_token

        return True

    # Invalid/expired token
    try:

        st.query_params.clear()

    except Exception:

        pass

    return False


# Restore login before deciding what to display.
restore_session_from_url()


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

    .main {
        padding-top: 1rem;
    }

    /* Brand */

    .brand-header {
        background: #111827;
        border-radius: 18px;
        padding: 28px 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .brand-title {
        color: white;
        font-size: 42px;
        font-weight: 800;
        margin: 0;
    }

    .brand-subtitle {
        color: #d1d5db;
        font-size: 16px;
        margin-top: 8px;
    }

    /* Login / signup */

    .auth-title {
        font-size: 32px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
    }

    .auth-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 20px;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        border-right: 1px solid #dbe3ea;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BRAND
# ============================================================

def show_brand():

    st.markdown(
        """
        <div class="brand-header">

            <div class="brand-title">
                🏗️ ConstructAI
            </div>

            <div class="brand-subtitle">
                Agentic Construction Risk Intelligence Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_signup_password(password):

    if len(password) < 8:
        return False

    if not any(
        char.isupper()
        for char in password
    ):
        return False

    if not any(
        char.islower()
        for char in password
    ):
        return False

    if not any(
        char.isdigit()
        for char in password
    ):
        return False

    return True


# ============================================================
# SIGN IN PAGE
# ============================================================

def show_sign_in():

    st.markdown(
        """
        <div class="auth-title">
            Welcome Back
        </div>

        <div class="auth-subtitle">
            Sign in using your username or registered email.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "login_form",
        clear_on_submit=False,
    ):

        identifier = st.text_input(
            "Username or Email",
            placeholder="Enter username or email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )

    if submitted:

        if not identifier.strip():

            st.error(
                "Please enter your username or email."
            )

            return

        if not password:

            st.error(
                "Please enter your password."
            )

            return

        success, result = login_user(
            identifier,
            password,
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if success:

            user = result

            session_token = create_login_session(
                user["id"]
            )

            st.session_state[
                "authenticated"
            ] = True

            st.session_state[
                "user_id"
            ] = user["id"]

            st.session_state[
                "full_name"
            ] = user["full_name"]

            st.session_state[
                "email"
            ] = user["email"]

            st.session_state[
                "username"
            ] = user["username"]

            st.session_state[
                "user_role"
            ] = user["role"]

            st.session_state[
                "session_token"
            ] = session_token

            # ------------------------------------------------
            # Store persistent session in URL.
            # ------------------------------------------------

            st.query_params["session"] = (
                session_token
            )

            st.rerun()

        # ----------------------------------------------------
        # INACTIVE ACCOUNT
        # ----------------------------------------------------

        elif result == "inactive":

            st.error(
                "This account is inactive. "
                "Please contact an administrator."
            )

        # ----------------------------------------------------
        # INVALID CREDENTIALS
        # ----------------------------------------------------

        else:

            st.error(
                "Invalid username/email or password."
            )


# ============================================================
# CREATE ACCOUNT PAGE
# ============================================================

def show_create_account():

    st.markdown(
        """
        <div class="auth-title">
            Create Account
        </div>

        <div class="auth-subtitle">
            Create a worker account for Construction-AI.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "create_account_form",
        clear_on_submit=False,
    ):

        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email",
        )

        username = st.text_input(
            "Username",
            placeholder="Choose a username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Minimum 8 characters",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
        )

        st.markdown(
            """
            <div style="
                background:#f5f6f8;
                padding:16px;
                border-radius:12px;
                margin-top:10px;
                margin-bottom:15px;
            ">
                <strong>Password requirements</strong>

                <br><br>

                • At least 8 characters<br>
                • At least one uppercase letter<br>
                • At least one lowercase letter<br>
                • At least one number

            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True,
        )

    if submitted:

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )

            return

        if not email.strip():

            st.error(
                "Please enter your email."
            )

            return

        if not username.strip():

            st.error(
                "Please choose a username."
            )

            return

        if not password:

            st.error(
                "Please enter a password."
            )

            return

        if password != confirm_password:

            st.error(
                "Passwords do not match."
            )

            return

        if not validate_signup_password(
            password
        ):

            st.error(
                "Password must contain at least "
                "8 characters, one uppercase letter, "
                "one lowercase letter, and one number."
            )

            return

        # ----------------------------------------------------
        # Public signup ALWAYS creates Worker.
        # ----------------------------------------------------

        success, result = create_user(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            role="Worker",
        )

        if success:

            st.success(
                "Account created successfully! "
                "You can now sign in."
            )

        else:

            st.error(
                result
            )


# ============================================================
# AUTHENTICATION SCREEN
# ============================================================

def show_authentication():

    show_brand()

    sign_in_tab, create_tab = st.tabs(
        [
            "🔐 Sign In",
            "📝 Create Account",
        ]
    )

    with sign_in_tab:

        show_sign_in()

    with create_tab:

        show_create_account()

    st.info(
        "New users can create an account using "
        "the 'Create Account' tab."
    )


# ============================================================
# LOGOUT
# ============================================================

def perform_logout():

    session_token = st.session_state.get(
        "session_token"
    )

    logout_user(
        session_token
    )

    try:

        st.query_params.clear()

    except Exception:

        pass

    st.session_state.clear()

    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="
                font-size:30px;
                font-weight:700;
                margin-bottom:5px;
            ">
                🏗️ ConstructAI
            </div>

            <div style="
                color:#6b7280;
                font-size:14px;
                margin-bottom:25px;
            ">
                Construction Risk Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        full_name = st.session_state.get(
            "full_name",
            "User",
        )

        username = st.session_state.get(
            "username",
            "",
        )

        role = st.session_state.get(
            "user_role",
            "Worker",
        )

        st.markdown(
            f"""
            **👤 {full_name}**

            `@{username}`

            **Role:** {role}
            """
        )

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
        ):

            perform_logout()


# ============================================================
# NAVIGATION
# ============================================================

def show_application():

    user_role = st.session_state.get(
        "user_role",
        "Worker",
    )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if user_role == "Admin":

        pages = [

            st.Page(
                "app_pages/admin_portal.py",
                title="Admin Portal",
                icon="👑",
                url_path="admin",
            ),

            st.Page(
                "app_pages/site_assessment.py",
                title="Site Assessment",
                icon="🚨",
                url_path="site-assessment",
            ),

            st.Page(
                "app_pages/dashboard.py",
                title="Executive Dashboard",
                icon="📊",
                url_path="executive-dashboard",
            ),

            st.Page(
                "app_pages/live_monitoring.py",
                title="Live Monitoring",
                icon="📹",
                url_path="live-monitoring",
            ),

            st.Page(
                "app_pages/inspection_history.py",
                title="Inspection History",
                icon="📋",
                url_path="inspection-history",
            ),
        ]

    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    elif user_role == "Manager":

        pages = [

            st.Page(
                "app_pages/site_assessment.py",
                title="Site Assessment",
                icon="🚨",
                url_path="site-assessment",
            ),

            st.Page(
                "app_pages/dashboard.py",
                title="Executive Dashboard",
                icon="📊",
                url_path="executive-dashboard",
            ),

            st.Page(
                "app_pages/live_monitoring.py",
                title="Live Monitoring",
                icon="📹",
                url_path="live-monitoring",
            ),

            st.Page(
                "app_pages/inspection_history.py",
                title="Inspection History",
                icon="📋",
                url_path="inspection-history",
            ),
        ]

    # --------------------------------------------------------
    # SAFETY OFFICER
    # --------------------------------------------------------

    elif user_role == "Safety Officer":

        pages = [

            st.Page(
                "app_pages/site_assessment.py",
                title="Site Assessment",
                icon="🚨",
                url_path="site-assessment",
            ),

            st.Page(
                "app_pages/live_monitoring.py",
                title="Live Monitoring",
                icon="📹",
                url_path="live-monitoring",
            ),

            st.Page(
                "app_pages/inspection_history.py",
                title="Inspection History",
                icon="📋",
                url_path="inspection-history",
            ),
        ]

    # --------------------------------------------------------
    # WORKER
    # --------------------------------------------------------

    else:

        pages = [

            st.Page(
                "app_pages/worker_portal.py",
                title="Worker Portal",
                icon="👷",
                url_path="worker",
            ),

            st.Page(
                "app_pages/site_assessment.py",
                title="Site Assessment",
                icon="🚨",
                url_path="site-assessment",
            ),

            st.Page(
                "app_pages/live_monitoring.py",
                title="Live Monitoring",
                icon="📹",
                url_path="live-monitoring",
            ),

            st.Page(
                "app_pages/inspection_history.py",
                title="Inspection History",
                icon="📋",
                url_path="inspection-history",
            ),
        ]

    # --------------------------------------------------------
    # CREATE NAVIGATION
    # --------------------------------------------------------

    pg = st.navigation(
        pages,
        position="sidebar",
    )

    pg.run()


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # NOT LOGGED IN
    # --------------------------------------------------------

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        show_authentication()

        return

    # --------------------------------------------------------
    # LOGGED IN
    # --------------------------------------------------------

    show_sidebar()

    show_application()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()