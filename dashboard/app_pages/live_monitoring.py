import threading
from pathlib import Path

import av
import cv2
import streamlit as st
from streamlit_webrtc import WebRtcMode, VideoProcessorBase, webrtc_streamer

from agents.safety_agent import SafetyAgent
from agents.safety_intelligence_agent import SafetyIntelligenceAgent
from agents.site_risk_agent import SiteRiskAgent
from utils.alerts import AlertManager
from utils.email_alerts import EmailAlertManager
from utils.database import save_live_alert
from utils.auth import restore_login_session


# ============================================================
# RESTORE LOGIN SESSION AFTER PAGE REFRESH
# ============================================================

if not st.session_state.get("authenticated", False):

    session_token = st.query_params.get("session")

    if session_token:
        restore_login_session(session_token)


# ============================================================
# LOGIN CHECK
# ============================================================

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ConstructAI | Live Monitoring",
    page_icon="🎥",
    layout="wide",
)


# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .hero {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #374151 100%);
        color: white;
        margin-bottom: 22px;
        border: 1px solid rgba(255,255,255,.08);
    }

    .hero-brand {
        font-size: 13px;
        letter-spacing: 2px;
        font-weight: 700;
        color: #93c5fd;
        margin-bottom: 7px;
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }

    .hero-subtitle {
        color: #d1d5db;
        margin-top: 8px;
        font-size: 15px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 750;
        margin: 22px 0 10px 0;
    }

    .status-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        min-height: 118px;
        box-shadow: 0 2px 10px rgba(0,0,0,.04);
    }

    .status-label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: .7px;
        font-weight: 700;
    }

    .status-value {
        font-size: 25px;
        font-weight: 800;
        margin-top: 8px;
        color: #111827;
    }

    .status-meta {
        font-size: 12px;
        color: #6b7280;
        margin-top: 5px;
    }

    .live-pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .7px;
        background: #fee2e2;
        color: #991b1b;
    }

    .pipeline {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 10px 0 20px 0;
    }

    .pipeline-step {
        padding: 9px 13px;
        border-radius: 9px;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        font-size: 12px;
        font-weight: 650;
        color: #374151;
    }

    .camera-shell {
        border: 1px solid #d1d5db;
        border-radius: 16px;
        padding: 10px;
        background: #f9fafb;
    }

    .info-card {
        padding: 16px 18px;
        border-radius: 13px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }

    .alert-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #fecaca;
        background: #fef2f2;
        margin-top: 8px;
    }

    .safe-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #bbf7d0;
        background: #f0fdf4;
        margin-top: 8px;
    }

    .small-muted {
        color: #6b7280;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-brand">CONSTRUCTAI • SAFETY INTELLIGENCE PLATFORM</div>
        <div class="hero-title">Live Safety Command Center</div>
        <div class="hero-subtitle">
            Real-time computer vision monitoring, worker protection intelligence,
            site-risk assessment and automatic safety alerts.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD AI AGENTS
# ============================================================

@st.cache_resource
def load_agents():
    return (
        SafetyAgent(),
        SafetyIntelligenceAgent(),
        SiteRiskAgent(),
    )


try:
    (
        safety_agent,
        safety_intelligence_agent,
        site_risk_agent,
    ) = load_agents()
except Exception as e:
    st.error("Unable to load the live-monitoring AI agents.")
    st.code(str(e))
    st.stop()


# ============================================================
# ALERT MANAGERS
# ============================================================

@st.cache_resource
def get_alert_manager():
    return AlertManager(cooldown_seconds=10)


@st.cache_resource
def get_email_alert_manager():
    return EmailAlertManager()


alert_manager = get_alert_manager()
email_alert_manager = get_email_alert_manager()


# ============================================================
# SHARED MONITORING STATE
# ============================================================

class MonitoringState:
    def __init__(self):
        self.lock = threading.Lock()

        self.workers_detected = 0
        self.violations = {
            "NO-Hardhat": 0,
            "NO-Mask": 0,
            "NO-Safety Vest": 0,
        }
        self.total_detections = 0
        self.site_status = "SAFE"

        self.worker_protection_level = "Good"
        self.safety_score = 100
        self.confirmed_violations = []
        self.safety_actions = []

        self.site_risk_level = "Low"
        self.site_risk_score = 0
        self.hazards = []
        self.site_actions = []

        self.safety_report = {}
        self.worker_protection_report = {}
        self.site_report = {}

        self.latest_alert = None


@st.cache_resource
def get_monitoring_state():
    return MonitoringState()


monitoring_state = get_monitoring_state()


# ============================================================
# PROJECT CONTEXT
# ============================================================

def get_project_context():
    analysis = st.session_state.get("analysis_result")

    if analysis:
        project_risk = analysis.get("project_risk", "Low")
        equipment_mttf = analysis.get("equipment_mttf", 1000)
        weather = analysis.get(
            "weather_prediction",
            analysis.get("weather", "Clear"),
        )

        return (
            project_risk,
            float(equipment_mttf),
            weather,
            True,
        )

    return (
        "Low",
        1000.0,
        "Clear",
        False,
    )


(
    project_risk,
    equipment_mttf,
    weather,
    context_available,
) = get_project_context()


# ============================================================
# VIDEO PROCESSOR
# ============================================================

class SafetyVideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.safety_agent = safety_agent
        self.safety_intelligence_agent = safety_intelligence_agent
        self.site_risk_agent = site_risk_agent

        self.project_risk = "Low"
        self.equipment_mttf = 1000.0
        self.weather = "Clear"

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")

        # ----------------------------------------------------
        # SAFETY AGENT
        # ----------------------------------------------------

        try:
            safety_report = self.safety_agent.inspect_frame(image)
        except Exception:
            return av.VideoFrame.from_ndarray(
                image,
                format="bgr24",
            )

        # ----------------------------------------------------
        # SAFETY INTELLIGENCE AGENT
        # ----------------------------------------------------

        try:
            worker_protection_report = (
                self.safety_intelligence_agent
                .analyze_worker_protection(safety_report)
            )
        except Exception:
            worker_protection_report = {
                "worker_protection_level": "Unknown",
                "safety_score": 0,
                "confirmed_violations": [],
                "recommended_actions": [],
                "workers_detected": 0,
            }

        # ----------------------------------------------------
        # SITE RISK AGENT
        # ----------------------------------------------------

        try:
            site_report = self.site_risk_agent.assess_site(
                self.project_risk,
                self.equipment_mttf,
                self.weather,
                safety_report,
            )
        except Exception:
            site_report = {
                "site_risk_level": "Low",
                "site_risk_score": 0,
                "hazards": [],
                "recommended_actions": [],
            }

        # ----------------------------------------------------
        # EXTRACT DATA
        # ----------------------------------------------------

        detections = safety_report.get("detections", [])
        violations = safety_report.get("violations", [])

        workers_detected = worker_protection_report.get(
            "workers_detected",
            0,
        )

        protection_level = worker_protection_report.get(
            "worker_protection_level",
            "Unknown",
        )

        safety_score = worker_protection_report.get(
            "safety_score",
            0,
        )

        confirmed_violations = worker_protection_report.get(
            "confirmed_violations",
            [],
        )

        safety_actions = worker_protection_report.get(
            "recommended_actions",
            [],
        )

        site_risk_level = site_report.get(
            "site_risk_level",
            "Low",
        )

        site_risk_score = site_report.get(
            "site_risk_score",
            0,
        )

        hazards = site_report.get("hazards", [])
        site_actions = site_report.get("recommended_actions", [])

        current_violations = {
            "NO-Hardhat": 0,
            "NO-Mask": 0,
            "NO-Safety Vest": 0,
        }

        for item in violations:
            label = item.get("label")
            confidence = float(item.get("confidence", 0))

            if (
                label in current_violations
                and confidence >= 0.50
            ):
                current_violations[label] += 1

        total_detections = len(detections)

        site_status = safety_report.get(
            "status",
            "SAFE",
        ).upper()

        # ----------------------------------------------------
        # AUTOMATIC ALERT SYSTEM
        # ----------------------------------------------------

        alert = alert_manager.check_alert(
            site_risk_level=site_risk_level,
            site_risk_score=site_risk_score,
            worker_protection_level=protection_level,
            safety_score=safety_score,
            violations=confirmed_violations,
        )

        # ----------------------------------------------------
        # EMAIL + DATABASE
        # ----------------------------------------------------

        if alert is not None:

            threading.Thread(
                target=email_alert_manager.send_alert,
                args=(alert,),
                daemon=True,
            ).start()

            try:
                save_live_alert(
                    alert=alert,
                    site_risk_level=site_risk_level,
                    site_risk_score=site_risk_score,
                    safety_score=safety_score,
                    worker_protection_level=protection_level,
                    workers_detected=workers_detected,
                    violations=confirmed_violations,
                    hazards=hazards,
                    recommended_actions=safety_actions + site_actions,
                )
            except Exception as e:
                print(
                    "Failed to save live alert to database:",
                    e,
                )

        # ----------------------------------------------------
        # UPDATE SHARED STATE
        # ----------------------------------------------------

        with monitoring_state.lock:
            monitoring_state.workers_detected = workers_detected
            monitoring_state.violations = dict(current_violations)
            monitoring_state.total_detections = total_detections
            monitoring_state.site_status = site_status

            monitoring_state.worker_protection_level = protection_level
            monitoring_state.safety_score = safety_score
            monitoring_state.confirmed_violations = list(
                confirmed_violations
            )
            monitoring_state.safety_actions = list(safety_actions)

            monitoring_state.site_risk_level = site_risk_level
            monitoring_state.site_risk_score = site_risk_score
            monitoring_state.hazards = list(hazards)
            monitoring_state.site_actions = list(site_actions)

            monitoring_state.safety_report = dict(safety_report)
            monitoring_state.worker_protection_report = dict(
                worker_protection_report
            )
            monitoring_state.site_report = dict(site_report)

            if alert is not None:
                monitoring_state.latest_alert = alert

        # ----------------------------------------------------
        # DRAW DETECTION BOXES
        # ----------------------------------------------------

        for item in detections:
            label = item.get("label", "Unknown")
            confidence = float(item.get("confidence", 0))
            box = item.get("box")

            if not box:
                continue

            x1, y1, x2, y2 = map(int, box)

            if label in current_violations:
                box_color = (0, 0, 255)
            else:
                box_color = (0, 255, 0)

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                box_color,
                2,
            )

            text = f"{label} {confidence:.2f}"

            cv2.putText(
                image,
                text,
                (
                    x1,
                    max(y1 - 10, 20),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                box_color,
                2,
            )

        # ----------------------------------------------------
        # CAMERA OVERLAY
        # ----------------------------------------------------

        if site_status == "UNSAFE":
            status_color = (0, 0, 255)
        else:
            status_color = (0, 255, 0)

        cv2.rectangle(
            image,
            (10, 10),
            (500, 80),
            (0, 0, 0),
            -1,
        )

        cv2.putText(
            image,
            f"SITE STATUS: {site_status}",
            (20, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            status_color,
            2,
        )

        cv2.rectangle(
            image,
            (10, 95),
            (500, 155),
            (0, 0, 0),
            -1,
        )

        cv2.putText(
            image,
            f"SITE RISK: {site_risk_level} ({site_risk_score}/100)",
            (20, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2,
        )

        total_violations = sum(current_violations.values())

        if total_violations > 0:
            cv2.rectangle(
                image,
                (10, 170),
                (520, 230),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                image,
                f"WARNING: {total_violations} PPE VIOLATION(S)",
                (20, 208),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        return av.VideoFrame.from_ndarray(
            image,
            format="bgr24",
        )


# ============================================================
# PROCESSOR FACTORY
# ============================================================

def processor_factory():
    processor = SafetyVideoProcessor()
    processor.project_risk = project_risk
    processor.equipment_mttf = equipment_mttf
    processor.weather = weather
    return processor


# ============================================================
# PROJECT CONTEXT BAR
# ============================================================

st.markdown(
    '<div class="section-title">Monitoring Context</div>',
    unsafe_allow_html=True,
)

context_cols = st.columns(4)

with context_cols[0]:
    st.metric("Project Risk", project_risk)

with context_cols[1]:
    st.metric("Equipment MTTF", f"{equipment_mttf:.1f}")

with context_cols[2]:
    st.metric("Weather", str(weather))

with context_cols[3]:
    if context_available:
        st.success("Assessment Linked")
    else:
        st.warning("Baseline Mode")


# ============================================================
# AI PIPELINE
# ============================================================

st.markdown(
    """
    <div class="pipeline">
        <div class="pipeline-step">🎥 Camera</div>
        <div class="pipeline-step">🤖 Safety Agent</div>
        <div class="pipeline-step">🦺 PPE Detection</div>
        <div class="pipeline-step">🧠 Safety Intelligence</div>
        <div class="pipeline-step">📊 Site Risk Agent</div>
        <div class="pipeline-step">🚨 Alert Manager</div>
        <div class="pipeline-step">📧 Email + SQLite</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CAMERA SECTION
# ============================================================

st.markdown(
    '<div class="section-title">Live Camera Feed</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="small-muted">
        Start the camera and allow browser access. The AI pipeline processes
        frames continuously and updates the safety intelligence panel below.
    </div>
    """,
    unsafe_allow_html=True,
)

if context_available:
    st.success(
        f"Linked to latest Site Assessment • "
        f"Project Risk: {project_risk} • "
        f"Equipment MTTF: {equipment_mttf:.1f} • "
        f"Weather: {weather}"
    )
else:
    st.warning(
        "No Site Assessment result is available. "
        "Live monitoring is using the default baseline."
    )

st.markdown('<div class="camera-shell">', unsafe_allow_html=True)

webrtc_streamer(
    key="constructai-live-monitoring",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=processor_factory,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
    video_html_attrs={
        "style": {
            "width": "600px",
            "height": "400px",
            "object-fit": "contain",
            "margin": "0 auto",
            "display": "block",
        },
        "controls": False,
        "autoPlay": True,
        "muted": True,
    },
    async_processing=True,
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# LIVE COMMAND CENTER
# ============================================================

st.markdown(
    '<div class="section-title">Live AI Safety Intelligence</div>',
    unsafe_allow_html=True,
)


@st.fragment(run_every="1s")
def live_safety_dashboard():

    with monitoring_state.lock:
        workers_detected = monitoring_state.workers_detected
        violations = dict(monitoring_state.violations)
        total_detections = monitoring_state.total_detections
        site_status = monitoring_state.site_status

        protection_level = monitoring_state.worker_protection_level
        safety_score = monitoring_state.safety_score
        confirmed_violations = list(
            monitoring_state.confirmed_violations
        )
        safety_actions = list(monitoring_state.safety_actions)

        site_risk_level = monitoring_state.site_risk_level
        site_risk_score = monitoring_state.site_risk_score
        hazards = list(monitoring_state.hazards)
        site_actions = list(monitoring_state.site_actions)

        latest_alert = monitoring_state.latest_alert

    # --------------------------------------------------------
    # STATUS HEADER
    # --------------------------------------------------------

    if site_status == "UNSAFE":
        st.error(
            f"🔴 LIVE STATUS: UNSAFE • "
            f"{workers_detected} worker(s) detected"
        )
    else:
        st.success(
            f"🟢 LIVE STATUS: {site_status} • "
            f"{workers_detected} worker(s) detected"
        )

    # --------------------------------------------------------
    # PRIMARY KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Workers Detected</div>
                <div class="status-value">{workers_detected}</div>
                <div class="status-meta">Real-time computer vision</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        total_violations = sum(violations.values())
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">PPE Violations</div>
                <div class="status-value">{total_violations}</div>
                <div class="status-meta">Confidence threshold ≥ 0.50</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Safety Score</div>
                <div class="status-value">{safety_score}/100</div>
                <div class="status-meta">{protection_level}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Site Risk</div>
                <div class="status-value">{site_risk_level}</div>
                <div class="status-meta">{site_risk_score}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PPE BREAKDOWN
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">PPE Detection Breakdown</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric("Worker Protection", protection_level)

    with p2:
        st.metric(
            "No Hardhat",
            violations.get("NO-Hardhat", 0),
        )

    with p3:
        st.metric(
            "No Mask",
            violations.get("NO-Mask", 0),
        )

    with p4:
        st.metric(
            "No Safety Vest",
            violations.get("NO-Safety Vest", 0),
        )

    # --------------------------------------------------------
    # TWO-COLUMN INTELLIGENCE
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-title">Confirmed PPE Violations</div>',
            unsafe_allow_html=True,
        )

        if confirmed_violations:
            for violation in confirmed_violations:
                st.error(f"⚠ {violation}")
        else:
            st.success("No confirmed PPE violations detected.")

        st.markdown(
            '<div class="section-title">Site Hazards</div>',
            unsafe_allow_html=True,
        )

        if hazards:
            for hazard in hazards:
                st.warning(hazard)
        else:
            st.success("No current site hazards identified.")

    with right:
        st.markdown(
            '<div class="section-title">Recommended Corrective Actions</div>',
            unsafe_allow_html=True,
        )

        all_actions = []

        for action in safety_actions + site_actions:
            if action not in all_actions:
                all_actions.append(action)

        if all_actions:
            for index, action in enumerate(all_actions, start=1):
                st.info(f"**{index}.** {action}")
        else:
            st.success("No corrective actions required at this moment.")

        st.markdown(
            '<div class="section-title">Detection Summary</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="info-card">
                <b>Total AI detections:</b> {total_detections}<br>
                <span class="small-muted">
                    Includes workers and PPE-related detections currently
                    returned by the Safety Agent.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # AUTOMATIC ALERTS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Automatic Safety Alerts</div>',
        unsafe_allow_html=True,
    )

    if latest_alert:
        if latest_alert["level"] == "CRITICAL":
            st.markdown(
                f"""
                <div class="alert-card">
                    <b>🚨 CRITICAL ALERT</b><br><br>
                    {latest_alert["message"]}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="alert-card">
                    <b>⚠️ WARNING</b><br><br>
                    {latest_alert["message"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            "The alert is subject to the configured cooldown to prevent "
            "repeated notifications from the same condition."
        )
    else:
        st.markdown(
            """
            <div class="safe-card">
                <b>✓ No active safety alerts</b><br>
                <span class="small-muted">
                    The automatic alert engine is monitoring the live feed.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # CURRENT RISK INTERPRETATION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Current Site Risk Interpretation</div>',
        unsafe_allow_html=True,
    )

    if site_risk_level == "High":
        st.error(
            "HIGH SITE RISK — Immediate corrective action is recommended."
        )
    elif site_risk_level == "Medium":
        st.warning(
            "MEDIUM SITE RISK — Review the detected hazards and "
            "recommended actions."
        )
    elif site_status == "UNSAFE":
        st.error(
            "PPE SAFETY VIOLATION DETECTED — Correct worker protection issues."
        )
    else:
        st.success(
            "Site currently appears safe based on the live AI assessment."
        )


live_safety_dashboard()


# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown("---")

with st.expander("How the ConstructAI live monitoring pipeline works"):

    st.markdown(
        """
        **1. Camera**  
        Browser camera provides the live video stream.

        **2. Safety Agent**  
        YOLO-based computer vision identifies workers and PPE violations.

        **3. Safety Intelligence Agent**  
        Converts detections into worker protection status and safety score.

        **4. Site Risk Agent**  
        Combines live safety information with project, equipment and weather
        context from the latest Site Assessment.

        **5. Alert Manager**  
        Determines whether a warning or critical alert should be generated.

        **6. Email + Database**  
        Resend sends the automatic notification and SQLite stores the live
        alert for later inspection-history review.

        The system monitors:
        - Construction workers
        - Missing hardhats
        - Missing masks
        - Missing safety vests
        - Worker protection level
        - Overall site risk
        - Safety hazards
        - Recommended corrective actions
        - Automatic email alerts
        - Live safety alerts stored in the database
        """
    )
