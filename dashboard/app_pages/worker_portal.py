import streamlit as st
from datetime import datetime

from utils.database import get_recent_live_alerts


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Worker Safety Portal",
    page_icon="👷",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-header {
        padding: 1.5rem 1.8rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 55%,
            #374151 100%
        );
        color: white;
        margin-bottom: 1.5rem;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }

    .main-header p {
        margin-top: 0.4rem;
        color: #d1d5db;
        font-size: 1rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .safety-card {
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        min-height: 125px;
    }

    .safety-card-title {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.4rem;
    }

    .safety-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }

    .safety-card-desc {
        font-size: 0.82rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }

    .rule-card {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        background: #f9fafb;
        border-left: 4px solid #374151;
        margin-bottom: 0.6rem;
    }

    .alert-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #fecaca;
        background: #fef2f2;
        margin-bottom: 0.8rem;
    }

    .alert-title {
        font-weight: 700;
        color: #991b1b;
    }

    .alert-message {
        margin-top: 0.3rem;
        color: #374151;
    }

    .footer-note {
        margin-top: 2rem;
        padding: 1rem;
        border-radius: 12px;
        background: #f3f4f6;
        color: #4b5563;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# USER INFORMATION
# ============================================================

username = st.session_state.get("username", "Worker")
role = st.session_state.get("user_role", "Worker")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div class="main-header">
        <h1>👷 Worker Safety Portal</h1>
        <p>
            Real-time safety information, PPE guidance, site alerts,
            and essential construction safety instructions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WORKER PROFILE
# ============================================================

st.markdown('<div class="section-title">👤 Worker Profile</div>', unsafe_allow_html=True)

profile_col1, profile_col2, profile_col3 = st.columns(3)

with profile_col1:
    st.markdown(
        f"""
        <div class="safety-card">
            <div class="safety-card-title">Logged-in User</div>
            <div class="safety-card-value">{username}</div>
            <div class="safety-card-desc">Authenticated worker</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with profile_col2:
    st.markdown(
        f"""
        <div class="safety-card">
            <div class="safety-card-title">Role</div>
            <div class="safety-card-value">{role}</div>
            <div class="safety-card-desc">Portal access level</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with profile_col3:
    st.markdown(
        f"""
        <div class="safety-card">
            <div class="safety-card-title">Safety Status</div>
            <div class="safety-card-value">Active</div>
            <div class="safety-card-desc">Follow all site instructions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")


# ============================================================
# PPE REQUIREMENTS
# ============================================================

st.markdown(
    '<div class="section-title">🦺 Required Personal Protective Equipment</div>',
    unsafe_allow_html=True,
)

ppe1, ppe2, ppe3 = st.columns(3)

with ppe1:
    st.markdown(
        """
        <div class="safety-card">
            <div class="safety-card-title">HEAD PROTECTION</div>
            <div class="safety-card-value">🪖 Hardhat</div>
            <div class="safety-card-desc">
                Required while working on the construction site.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with ppe2:
    st.markdown(
        """
        <div class="safety-card">
            <div class="safety-card-title">BODY PROTECTION</div>
            <div class="safety-card-value">🦺 Safety Vest</div>
            <div class="safety-card-desc">
                Wear high-visibility protection in work areas.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with ppe3:
    st.markdown(
        """
        <div class="safety-card">
            <div class="safety-card-title">RESPIRATORY PROTECTION</div>
            <div class="safety-card-value">😷 Mask</div>
            <div class="safety-card-desc">
                Use where site conditions require it.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAFETY STATUS
# ============================================================

st.markdown(
    '<div class="section-title">🛡️ Current Safety Status</div>',
    unsafe_allow_html=True,
)

status_col1, status_col2 = st.columns([1, 2])

with status_col1:
    st.success("### 🟢 Safety Ready")

with status_col2:
    st.info(
        "Before starting work, make sure all required PPE is worn "
        "and follow the instructions provided by the site safety officer."
    )


# ============================================================
# RECENT LIVE ALERTS
# ============================================================

st.markdown(
    '<div class="section-title">🚨 Recent Site Safety Alerts</div>',
    unsafe_allow_html=True,
)

try:
    alerts = get_recent_live_alerts(limit=5)
except Exception:
    alerts = []


if alerts:

    for alert in alerts:

        if isinstance(alert, dict):
            level = alert.get("alert_level", "WARNING")
            message = alert.get(
                "alert_message",
                "Safety alert detected.",
            )
            created_at = alert.get("created_at", "")
        else:
            level = "WARNING"
            message = str(alert)
            created_at = ""

        if level == "CRITICAL":
            st.error(
                f"🚨 **CRITICAL ALERT**\n\n"
                f"{message}"
            )

        else:
            st.warning(
                f"⚠️ **SAFETY WARNING**\n\n"
                f"{message}"
            )

        if created_at:
            st.caption(f"Alert time: {created_at}")

else:

    st.success(
        "🟢 No recent safety alerts have been recorded."
    )


# ============================================================
# SAFETY INSTRUCTIONS
# ============================================================

st.markdown(
    '<div class="section-title">📋 Essential Site Safety Rules</div>',
    unsafe_allow_html=True,
)

rules = [
    "Wear the required hardhat at all times.",
    "Wear a high-visibility safety vest.",
    "Use the required mask where applicable.",
    "Follow instructions from the site safety officer.",
    "Report unsafe conditions immediately.",
    "Do not continue work when a serious safety hazard is identified.",
]

for index, rule in enumerate(rules, start=1):

    st.markdown(
        f"""
        <div class="rule-card">
            <strong>{index}.</strong> {rule}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# WHAT TO DO IF A HAZARD IS FOUND
# ============================================================

st.markdown(
    '<div class="section-title">⚠️ If You Identify a Hazard</div>',
    unsafe_allow_html=True,
)

hazard_col1, hazard_col2, hazard_col3 = st.columns(3)

with hazard_col1:
    st.markdown(
        """
        ### 1️⃣ Stop
        Stop work if an immediate serious safety hazard is present.
        """
    )

with hazard_col2:
    st.markdown(
        """
        ### 2️⃣ Move to Safety
        Move away from dangerous equipment, areas, or conditions.
        """
    )

with hazard_col3:
    st.markdown(
        """
        ### 3️⃣ Report
        Inform the site safety officer immediately.
        """
    )


# ============================================================
# IMPORTANT NOTICE
# ============================================================

st.markdown(
    '<div class="section-title">📢 Important Safety Notice</div>',
    unsafe_allow_html=True,
)

st.warning(
    "If you notice an unsafe condition, PPE issue, equipment problem, "
    "or other serious hazard, immediately inform the site safety officer "
    "and follow the site's emergency procedures."
)


# ============================================================
# FOOTER
# ============================================================

current_time = datetime.now().strftime("%d %b %Y, %H:%M")

st.markdown(
    f"""
    <div class="footer-note">
        <strong>ConstructAI Worker Safety Portal</strong><br>
        Safety information is provided for site awareness and should
        be used together with official site safety procedures.<br><br>
        Last portal refresh: {current_time}
    </div>
    """,
    unsafe_allow_html=True,
)