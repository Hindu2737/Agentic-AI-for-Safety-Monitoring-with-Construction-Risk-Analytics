import threading
from pathlib import Path

import av
import cv2
import streamlit as st
from streamlit_webrtc import (
    WebRtcMode,
    VideoProcessorBase,
    webrtc_streamer,
)

from agents.safety_agent import SafetyAgent
from agents.safety_intelligence_agent import (
    SafetyIntelligenceAgent,
)
from agents.site_risk_agent import SiteRiskAgent
from utils.alerts import AlertManager


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.title("📹 Real-Time Site Monitoring")

st.caption(
    "AI-powered real-time construction site monitoring "
    "using Safety Agent, Safety Intelligence Agent, "
    "Site Risk Agent and automatic alerts."
)


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# LOAD AI AGENTS
# ============================================================

@st.cache_resource
def load_agents():

    safety_agent = SafetyAgent()

    safety_intelligence_agent = (
        SafetyIntelligenceAgent()
    )

    site_risk_agent = SiteRiskAgent()

    return (
        safety_agent,
        safety_intelligence_agent,
        site_risk_agent,
    )


try:

    (
        safety_agent,
        safety_intelligence_agent,
        site_risk_agent,
    ) = load_agents()

except Exception as e:

    st.error(
        "❌ Unable to load AI agents."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# LOAD ALERT MANAGER
# ============================================================

@st.cache_resource
def get_alert_manager():

    return AlertManager(
        cooldown_seconds=10
    )


alert_manager = get_alert_manager()


# ============================================================
# SHARED MONITORING STATE
# ============================================================

class MonitoringState:

    def __init__(self):

        self.lock = threading.Lock()

        # ----------------------------------------------------
        # Safety Agent
        # ----------------------------------------------------

        self.workers_detected = 0

        self.violations = {
            "NO-Hardhat": 0,
            "NO-Mask": 0,
            "NO-Safety Vest": 0,
        }

        self.total_detections = 0

        self.site_status = "SAFE"

        # ----------------------------------------------------
        # Safety Intelligence
        # ----------------------------------------------------

        self.worker_protection_level = "Good"

        self.safety_score = 100

        self.confirmed_violations = []

        self.safety_actions = []

        # ----------------------------------------------------
        # Site Risk
        # ----------------------------------------------------

        self.site_risk_level = "Low"

        self.site_risk_score = 0

        self.hazards = []

        self.site_actions = []

        # ----------------------------------------------------
        # Agent reports
        # ----------------------------------------------------

        self.safety_report = {}

        self.worker_protection_report = {}

        self.site_report = {}

        # ----------------------------------------------------
        # Automatic alert
        # ----------------------------------------------------

        self.latest_alert = None


@st.cache_resource
def get_monitoring_state():

    return MonitoringState()


monitoring_state = get_monitoring_state()


# ============================================================
# PROJECT CONTEXT
# ============================================================

def get_project_context():

    analysis = st.session_state.get(
        "analysis_result"
    )

    if analysis:

        project_risk = analysis.get(
            "project_risk",
            "Low",
        )

        equipment_mttf = analysis.get(
            "equipment_mttf",
            1000,
        )

        weather = analysis.get(
            "weather_prediction",
            analysis.get(
                "weather",
                "Clear",
            ),
        )

        return (
            project_risk,
            float(equipment_mttf),
            weather,
            True,
        )

    # --------------------------------------------------------
    # Default baseline
    # --------------------------------------------------------

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

        self.safety_intelligence_agent = (
            safety_intelligence_agent
        )

        self.site_risk_agent = (
            site_risk_agent
        )

        self.project_risk = "Low"

        self.equipment_mttf = 1000.0

        self.weather = "Clear"


    def recv(self, frame):

        # ====================================================
        # CONVERT FRAME
        # ====================================================

        image = frame.to_ndarray(
            format="bgr24"
        )


        # ====================================================
        # SAFETY AGENT
        # ====================================================

        try:

            safety_report = (
                self.safety_agent.inspect_frame(
                    image
                )
            )

        except Exception:

            return av.VideoFrame.from_ndarray(
                image,
                format="bgr24",
            )


        # ====================================================
        # SAFETY INTELLIGENCE AGENT
        # ====================================================

        try:

            worker_protection_report = (
                self.safety_intelligence_agent
                .analyze_worker_protection(
                    safety_report
                )
            )

        except Exception as e:

            worker_protection_report = {

                "worker_protection_level":
                    "Unknown",

                "safety_score":
                    0,

                "confirmed_violations":
                    [],

                "recommended_actions":
                    [],

                "workers_detected":
                    0,
            }


        # ====================================================
        # SITE RISK AGENT
        # ====================================================

        try:

            site_report = (
                self.site_risk_agent.assess_site(
                    self.project_risk,
                    self.equipment_mttf,
                    self.weather,
                    safety_report,
                )
            )

        except Exception:

            site_report = {

                "site_risk_level":
                    "Low",

                "site_risk_score":
                    0,

                "hazards":
                    [],

                "recommended_actions":
                    [],
            }


        # ====================================================
        # EXTRACT SAFETY DATA
        # ====================================================

        detections = safety_report.get(
            "detections",
            [],
        )

        violations = safety_report.get(
            "violations",
            [],
        )


        # ====================================================
        # WORKER PROTECTION DATA
        # ====================================================

        workers_detected = (
            worker_protection_report.get(
                "workers_detected",
                0,
            )
        )

        protection_level = (
            worker_protection_report.get(
                "worker_protection_level",
                "Unknown",
            )
        )

        safety_score = (
            worker_protection_report.get(
                "safety_score",
                0,
            )
        )

        confirmed_violations = (
            worker_protection_report.get(
                "confirmed_violations",
                [],
            )
        )

        safety_actions = (
            worker_protection_report.get(
                "recommended_actions",
                [],
            )
        )


        # ====================================================
        # SITE RISK DATA
        # ====================================================

        site_risk_level = (
            site_report.get(
                "site_risk_level",
                "Low",
            )
        )

        site_risk_score = (
            site_report.get(
                "site_risk_score",
                0,
            )
        )

        hazards = (
            site_report.get(
                "hazards",
                [],
            )
        )

        site_actions = (
            site_report.get(
                "recommended_actions",
                [],
            )
        )


        # ====================================================
        # PPE VIOLATION COUNTS
        # ====================================================

        current_violations = {

            "NO-Hardhat": 0,

            "NO-Mask": 0,

            "NO-Safety Vest": 0,
        }


        for item in violations:

            label = item.get(
                "label"
            )

            confidence = float(
                item.get(
                    "confidence",
                    0,
                )
            )

            if (
                label in current_violations
                and confidence >= 0.50
            ):

                current_violations[
                    label
                ] += 1


        # ====================================================
        # TOTAL DETECTIONS
        # ====================================================

        total_detections = len(
            detections
        )


        # ====================================================
        # SITE STATUS
        # ====================================================

        site_status = safety_report.get(
            "status",
            "SAFE",
        ).upper()


        # ====================================================
        # AUTOMATIC ALERT SYSTEM
        # ====================================================

        alert = alert_manager.check_alert(

            site_risk_level=
                site_risk_level,

            site_risk_score=
                site_risk_score,

            worker_protection_level=
                protection_level,

            safety_score=
                safety_score,

            violations=
                confirmed_violations,
        )


        # ====================================================
        # UPDATE SHARED STATE
        # ====================================================

        with monitoring_state.lock:

            monitoring_state.workers_detected = (
                workers_detected
            )

            monitoring_state.violations = dict(
                current_violations
            )

            monitoring_state.total_detections = (
                total_detections
            )

            monitoring_state.site_status = (
                site_status
            )

            monitoring_state.worker_protection_level = (
                protection_level
            )

            monitoring_state.safety_score = (
                safety_score
            )

            monitoring_state.confirmed_violations = list(
                confirmed_violations
            )

            monitoring_state.safety_actions = list(
                safety_actions
            )

            monitoring_state.site_risk_level = (
                site_risk_level
            )

            monitoring_state.site_risk_score = (
                site_risk_score
            )

            monitoring_state.hazards = list(
                hazards
            )

            monitoring_state.site_actions = list(
                site_actions
            )

            monitoring_state.safety_report = dict(
                safety_report
            )

            monitoring_state.worker_protection_report = (
                dict(
                    worker_protection_report
                )
            )

            monitoring_state.site_report = dict(
                site_report
            )

            # ----------------------------------------------
            # SAVE ALERT
            # ----------------------------------------------

            if alert is not None:

                monitoring_state.latest_alert = (
                    alert
                )


        # ====================================================
        # DRAW DETECTION BOXES
        # ====================================================

        for item in detections:

            label = item.get(
                "label",
                "Unknown",
            )

            confidence = float(
                item.get(
                    "confidence",
                    0,
                )
            )

            box = item.get(
                "box"
            )

            if not box:
                continue


            x1, y1, x2, y2 = map(
                int,
                box,
            )


            # ------------------------------------------------
            # PPE = RED
            # ------------------------------------------------

            if label in current_violations:

                box_color = (
                    0,
                    0,
                    255,
                )

            # ------------------------------------------------
            # NORMAL = GREEN
            # ------------------------------------------------

            else:

                box_color = (
                    0,
                    255,
                    0,
                )


            cv2.rectangle(

                image,

                (x1, y1),

                (x2, y2),

                box_color,

                2,
            )


            text = (
                f"{label} "
                f"{confidence:.2f}"
            )


            cv2.putText(

                image,

                text,

                (
                    x1,
                    max(
                        y1 - 10,
                        20,
                    ),
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                box_color,

                2,
            )


        # ====================================================
        # STATUS COLOR
        # ====================================================

        if site_status == "UNSAFE":

            status_color = (
                0,
                0,
                255,
            )

        else:

            status_color = (
                0,
                255,
                0,
            )


        # ====================================================
        # SITE STATUS OVERLAY
        # ====================================================

        cv2.rectangle(

            image,

            (10, 10),

            (470, 80),

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


        # ====================================================
        # SITE RISK OVERLAY
        # ====================================================

        cv2.rectangle(

            image,

            (10, 95),

            (500, 155),

            (0, 0, 0),

            -1,
        )


        cv2.putText(

            image,

            (
                f"SITE RISK: "
                f"{site_risk_level} "
                f"({site_risk_score}/100)"
            ),

            (20, 135),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            status_color,

            2,
        )


        # ====================================================
        # PPE WARNING
        # ====================================================

        total_violations = sum(
            current_violations.values()
        )


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

                (
                    f"WARNING: "
                    f"{total_violations} "
                    f"PPE VIOLATION(S)"
                ),

                (20, 208),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0, 0, 255),

                2,
            )


        # ====================================================
        # RETURN PROCESSED FRAME
        # ====================================================

        return av.VideoFrame.from_ndarray(

            image,

            format="bgr24",
        )


# ============================================================
# PROCESSOR FACTORY
# ============================================================

def processor_factory():

    processor = SafetyVideoProcessor()

    processor.project_risk = (
        project_risk
    )

    processor.equipment_mttf = (
        equipment_mttf
    )

    processor.weather = (
        weather
    )

    return processor


# ============================================================
# CAMERA SECTION
# ============================================================

st.subheader("🎥 Live Camera")


st.info(
    "Click START and allow camera access when "
    "your browser asks for permission."
)


if context_available:

    st.success(

        f"Using latest Site Assessment context: "
        f"Project Risk = {project_risk} | "
        f"Equipment MTTF = {equipment_mttf:.1f} | "
        f"Weather = {weather}"
    )

else:

    st.warning(

        "No Site Assessment result is available yet. "
        "Live monitoring is using the default baseline: "
        "Low project risk, MTTF 1000 and Clear weather."
    )


# ============================================================
# WEBRTC CAMERA
# ============================================================

webrtc_streamer(

    key="constructai-live-monitoring",

    mode=WebRtcMode.SENDRECV,

    video_processor_factory=
        processor_factory,

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


# ============================================================
# LIVE DASHBOARD
# ============================================================

st.markdown("---")


@st.fragment(run_every="1s")
def live_safety_dashboard():

    st.subheader(
        "🚨 Live AI Safety Intelligence"
    )


    # ========================================================
    # READ SHARED STATE
    # ========================================================

    with monitoring_state.lock:

        workers_detected = (
            monitoring_state.workers_detected
        )

        violations = dict(
            monitoring_state.violations
        )

        total_detections = (
            monitoring_state.total_detections
        )

        site_status = (
            monitoring_state.site_status
        )

        protection_level = (
            monitoring_state.worker_protection_level
        )

        safety_score = (
            monitoring_state.safety_score
        )

        confirmed_violations = list(
            monitoring_state.confirmed_violations
        )

        safety_actions = list(
            monitoring_state.safety_actions
        )

        site_risk_level = (
            monitoring_state.site_risk_level
        )

        site_risk_score = (
            monitoring_state.site_risk_score
        )

        hazards = list(
            monitoring_state.hazards
        )

        site_actions = list(
            monitoring_state.site_actions
        )

        latest_alert = (
            monitoring_state.latest_alert
        )


    # ========================================================
    # MAIN METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "👷 Workers",
            workers_detected,
        )


    with col2:

        total_violations = sum(
            violations.values()
        )

        st.metric(
            "⚠️ PPE Violations",
            total_violations,
        )


    with col3:

        st.metric(
            "🛡️ Safety Score",
            f"{safety_score}/100",
        )


    with col4:

        st.metric(
            "🚨 Site Risk",
            site_risk_level,
            f"{site_risk_score}/100",
        )


    # ========================================================
    # AI PROTECTION ASSESSMENT
    # ========================================================

    st.markdown(
        "### AI Protection Assessment"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Worker Protection",
            protection_level,
        )


    with col2:

        st.metric(
            "No Hardhat",
            violations.get(
                "NO-Hardhat",
                0,
            ),
        )


    with col3:

        st.metric(
            "No Mask",
            violations.get(
                "NO-Mask",
                0,
            ),
        )


    with col4:

        st.metric(
            "No Safety Vest",
            violations.get(
                "NO-Safety Vest",
                0,
            ),
        )


    # ========================================================
    # CONFIRMED VIOLATIONS
    # ========================================================

    if confirmed_violations:

        st.subheader(
            "❌ Confirmed PPE Violations"
        )

        for violation in confirmed_violations:

            st.error(
                f"• {violation}"
            )

    else:

        st.success(
            "✅ No confirmed PPE violations detected."
        )


    # ========================================================
    # HAZARDS
    # ========================================================

    if hazards:

        st.subheader(
            "⚠️ Site Hazards"
        )

        for hazard in hazards:

            st.warning(
                f"• {hazard}"
            )


    # ========================================================
    # RECOMMENDED ACTIONS
    # ========================================================

    all_actions = []


    for action in (
        safety_actions + site_actions
    ):

        if action not in all_actions:

            all_actions.append(
                action
            )


    if all_actions:

        st.subheader(
            "🛠️ Recommended Actions"
        )

        for action in all_actions:

            st.info(
                f"• {action}"
            )


    # ========================================================
    # AUTOMATIC ALERT
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🚨 Automatic AI Alerts"
    )


    if latest_alert:

        if latest_alert["level"] == "CRITICAL":

            st.error(

                f"🚨 CRITICAL ALERT\n\n"
                f"{latest_alert['message']}"
            )

        else:

            st.warning(

                f"⚠️ WARNING\n\n"
                f"{latest_alert['message']}"
            )

    else:

        st.success(
            "✅ No active safety alerts."
        )


    # ========================================================
    # CURRENT SITE STATUS
    # ========================================================

    if site_risk_level == "High":

        st.error(
            "🚨 HIGH SITE RISK — Immediate "
            "corrective action is recommended."
        )

    elif site_risk_level == "Medium":

        st.warning(
            "⚠️ MEDIUM SITE RISK — Review the "
            "detected hazards and recommended actions."
        )

    elif site_status == "UNSAFE":

        st.error(
            "🚨 PPE SAFETY VIOLATION DETECTED — "
            "Correct worker protection issues."
        )

    else:

        st.success(
            "✅ Site currently appears safe based "
            "on the live AI assessment."
        )


# ============================================================
# RUN LIVE DASHBOARD
# ============================================================

live_safety_dashboard()


# ============================================================
# HOW IT WORKS
# ============================================================

with st.expander(
    "ℹ️ How the AI Monitoring Pipeline Works"
):

    st.write(
        """
        Camera
            ↓
        Safety Agent
            ↓
        YOLO PPE Detection
            ↓
        Safety Intelligence Agent
            ↓
        Worker Protection Score
            ↓
        Site Risk Agent
            ↓
        Site Risk Score
            ↓
        Alert Manager
            ↓
        Automatic Safety Alert

        The system monitors:

        • Construction workers
        • Missing hardhats
        • Missing masks
        • Missing safety vests
        • Worker protection level
        • Overall site risk
        • Safety hazards
        • Recommended corrective actions
        """
    )