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
    login_user,
    logout_user,
    is_authenticated,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ConstructAI | Site Safety Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

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
# LOGIN PAGE
# ============================================================

if not is_authenticated():

    st.title("🏗️ ConstructAI")

    st.subheader("Agentic Construction Risk Intelligence Platform")

    st.markdown(
        "### 🔐 Secure Login"
    )

    st.caption(
        "Sign in to access the Construction-AI platform."
    )

    with st.form("login_form"):

        username = st.text_input(
            "Username",
            placeholder="Enter username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "🔐 Login",
            use_container_width=True,
        )

        if submitted:

            if login_user(username, password):

                st.success("Login successful.")

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.divider()

    st.caption(
        "Authorized users only."
    )

    st.stop()


# ============================================================
# LOGGED-IN USER INFORMATION
# ============================================================

username = st.session_state.get("username")
role = st.session_state.get("user_role")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🏗️ ConstructAI")

    st.markdown(
        f"**User:** {username}"
    )

    st.markdown(
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
# WORKER PORTAL
# ============================================================

if role == "Worker":

    worker_page = st.Page(
        "app_pages/worker_portal.py",
        title="Worker Safety Portal",
        icon=":material/engineering:",
    )

    worker_page.run()

    st.stop()


# ============================================================
# MANAGEMENT / SAFETY NAVIGATION
# ============================================================

pages = []


# ------------------------------------------------------------
# ADMIN
# ------------------------------------------------------------

if role == "Admin":

    pages = [
        st.Page(
            "app_pages/site_assessment.py",
            title="Site Assessment",
            icon=":material/health_and_safety:",
        ),
        st.Page(
            "app_pages/dashboard.py",
            title="Executive Dashboard",
            icon=":material/dashboard:",
        ),
        st.Page(
            "app_pages/live_monitoring.py",
            title="Live Monitoring",
            icon=":material/videocam:",
        ),
        st.Page(
            "app_pages/inspection_history.py",
            title="Inspection History",
            icon=":material/history:",
        ),
    ]


# ------------------------------------------------------------
# PROJECT MANAGER
# ------------------------------------------------------------

elif role == "Project Manager":

    pages = [
        st.Page(
            "app_pages/site_assessment.py",
            title="Site Assessment",
            icon=":material/health_and_safety:",
        ),
        st.Page(
            "app_pages/dashboard.py",
            title="Executive Dashboard",
            icon=":material/dashboard:",
        ),
        st.Page(
            "app_pages/inspection_history.py",
            title="Inspection History",
            icon=":material/history:",
        ),
    ]


# ------------------------------------------------------------
# SAFETY OFFICER
# ------------------------------------------------------------

elif role == "Safety Officer":

    pages = [
        st.Page(
            "app_pages/site_assessment.py",
            title="Site Assessment",
            icon=":material/health_and_safety:",
        ),
        st.Page(
            "app_pages/dashboard.py",
            title="Executive Dashboard",
            icon=":material/dashboard:",
        ),
        st.Page(
            "app_pages/live_monitoring.py",
            title="Live Monitoring",
            icon=":material/videocam:",
        ),
        st.Page(
            "app_pages/inspection_history.py",
            title="Inspection History",
            icon=":material/history:",
        ),
    ]


# ============================================================
# NAVIGATION
# ============================================================

if pages:

    page = st.navigation(
        pages,
        position="top",
    )

    page.run()