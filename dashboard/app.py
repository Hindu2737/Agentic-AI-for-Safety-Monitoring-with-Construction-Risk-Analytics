import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# AUTHENTICATION
# ============================================================

from utils.auth import (
    initialize_users_table,
    create_user,
    login_user,
    logout_user,
    is_authenticated,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ConstructAI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_users_table()


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "full_name" not in st.session_state:
    st.session_state["full_name"] = None

if "email" not in st.session_state:
    st.session_state["email"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

if "dashboard_analysis_result" not in st.session_state:
    st.session_state["dashboard_analysis_result"] = None

if "last_saved_inspection_id" not in st.session_state:
    st.session_state["last_saved_inspection_id"] = None


# ============================================================
# LOGIN / SIGNUP PAGE
# ============================================================

if not is_authenticated():

    # --------------------------------------------------------
    # CUSTOM LOGIN CSS
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        .auth-header {
            max-width: 700px;
            margin: 3rem auto 2rem auto;
            padding: 2.5rem;
            border-radius: 22px;
            background: linear-gradient(
                135deg,
                #111827,
                #1f2937
            );
            color: white;
            text-align: center;
        }

        .auth-title {
            font-size: 2.7rem;
            font-weight: 800;
            margin: 0;
        }

        .auth-subtitle {
            font-size: 1rem;
            color: #d1d5db;
            margin-top: 0.7rem;
        }

        .security-note {
            padding: 1rem;
            border-radius: 12px;
            background: #f3f4f6;
            margin-top: 1rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="auth-header">
            <div class="auth-title">
                🏗️ ConstructAI
            </div>
            <div class="auth-subtitle">
                Agentic Construction Risk Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SIGN IN / SIGN UP TABS
    # --------------------------------------------------------

    signin_tab, signup_tab = st.tabs(
        [
            "🔐 Sign In",
            "📝 Create Account",
        ]
    )

    # ========================================================
    # SIGN IN TAB
    # ========================================================

    with signin_tab:

        st.subheader("Welcome Back")

        st.caption(
            "Sign in using your username or registered email."
        )

        login_identifier = st.text_input(
            "Username or Email",
            placeholder="Enter username or email",
            key="login_identifier",
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password",
        )

        st.write("")

        login_button = st.button(
            "Sign In",
            use_container_width=True,
            type="primary",
            key="signin_button",
        )

        if login_button:

            if not login_identifier or not login_password:

                st.error(
                    "Please enter your username/email and password."
                )

            else:

                login_success = login_user(
                    login_identifier,
                    login_password,
                )

                if login_success:

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid username/email or password."
                    )

        st.info(
            "New users can create an account using the "
            "'Create Account' tab."
        )

    # ========================================================
    # SIGN UP TAB
    # ========================================================

    with signup_tab:

        st.subheader("Create Your Account")

        st.caption(
            "Create a new ConstructAI account."
        )

        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="signup_full_name",
        )

        email = st.text_input(
            "Email",
            placeholder="example@email.com",
            key="signup_email",
        )

        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Minimum 8 characters",
            key="signup_password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm_password",
        )

        st.markdown(
            """
            <div class="security-note">
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

        st.write("")

        signup_button = st.button(
            "Create Account",
            use_container_width=True,
            type="primary",
            key="signup_button",
        )

        if signup_button:

            if not full_name:
                st.error(
                    "Please enter your full name."
                )

            elif not email:
                st.error(
                    "Please enter your email."
                )

            elif not username:
                st.error(
                    "Please choose a username."
                )

            elif not password:
                st.error(
                    "Please enter a password."
                )

            elif password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = create_user(
                    full_name=full_name,
                    email=email,
                    username=username,
                    password=password,
                    role="Worker",
                )

                if success:

                    st.success(message)

                    st.info(
                        "Your account has been created as a Worker. "
                        "Go to the Sign In tab to access your account."
                    )

                else:

                    st.error(message)

    st.stop()


# ============================================================
# LOGGED-IN USER
# ============================================================

username = st.session_state.get(
    "username",
    "User",
)

full_name = st.session_state.get(
    "full_name",
    username,
)

role = st.session_state.get(
    "user_role",
    "Worker",
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🏗️ ConstructAI")

    st.caption(
        "Construction Risk Intelligence"
    )

    st.divider()

    st.markdown("### 👤 Account")

    st.write(
        f"**Name:** {full_name}"
    )

    st.write(
        f"**Username:** {username}"
    )

    st.write(
        f"**Role:** {role}"
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        logout_user()

        st.rerun()


# ============================================================
# ROLE-BASED NAVIGATION
# ============================================================


# ============================================================
# WORKER
# ============================================================

if role == "Worker":

    worker_page = st.Page(
        "app_pages/worker_portal.py",
        title="Worker Safety Portal",
        icon="👷",
        default=True,
    )

    pg = st.navigation(
        [worker_page],
        position="sidebar",
    )

    pg.run()


# ============================================================
# ADMIN
# ============================================================

elif role == "Admin":

    site_assessment_page = st.Page(
        "app_pages/site_assessment.py",
        title="Site Assessment",
        icon="🦺",
    )

    dashboard_page = st.Page(
        "app_pages/dashboard.py",
        title="Executive Dashboard",
        icon="📊",
    )

    live_monitoring_page = st.Page(
        "app_pages/live_monitoring.py",
        title="Live Monitoring",
        icon="📹",
    )

    inspection_history_page = st.Page(
        "app_pages/inspection_history.py",
        title="Inspection History",
        icon="📋",
    )

    pg = st.navigation(
        [
            site_assessment_page,
            dashboard_page,
            live_monitoring_page,
            inspection_history_page,
        ],
        position="sidebar",
    )

    pg.run()


# ============================================================
# PROJECT MANAGER
# ============================================================

elif role == "Project Manager":

    site_assessment_page = st.Page(
        "app_pages/site_assessment.py",
        title="Site Assessment",
        icon="🦺",
    )

    dashboard_page = st.Page(
        "app_pages/dashboard.py",
        title="Executive Dashboard",
        icon="📊",
    )

    inspection_history_page = st.Page(
        "app_pages/inspection_history.py",
        title="Inspection History",
        icon="📋",
    )

    pg = st.navigation(
        [
            site_assessment_page,
            dashboard_page,
            inspection_history_page,
        ],
        position="sidebar",
    )

    pg.run()


# ============================================================
# SAFETY OFFICER
# ============================================================

elif role == "Safety Officer":

    site_assessment_page = st.Page(
        "app_pages/site_assessment.py",
        title="Site Assessment",
        icon="🦺",
    )

    dashboard_page = st.Page(
        "app_pages/dashboard.py",
        title="Executive Dashboard",
        icon="📊",
    )

    live_monitoring_page = st.Page(
        "app_pages/live_monitoring.py",
        title="Live Monitoring",
        icon="📹",
    )

    inspection_history_page = st.Page(
        "app_pages/inspection_history.py",
        title="Inspection History",
        icon="📋",
    )

    pg = st.navigation(
        [
            site_assessment_page,
            dashboard_page,
            live_monitoring_page,
            inspection_history_page,
        ],
        position="sidebar",
    )

    pg.run()


# ============================================================
# INVALID ROLE
# ============================================================

else:

    st.error(
        "Your account does not have a valid role."
    )

    if st.button("Logout"):

        logout_user()

        st.rerun()