from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from agents.project_agent import ProjectAgent
from agents.resource_agent import ResourceAgent
from agents.weather_agent import WeatherAgent
from agents.safety_agent import SafetyAgent
from agents.site_risk_agent import SiteRiskAgent
from agents.safety_intelligence_agent import SafetyIntelligenceAgent
from agents.compliance_agent import ComplianceAgent
from agents.insurance_agent import InsuranceIntelligenceAgent

from utils.database import save_inspection


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ConstructAI | Site Assessment",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.7rem 2rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e293b 55%,
            #334155 100%
        );
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.15rem;
        font-weight: 800;
    }

    .hero p {
        margin: .35rem 0 0;
        color: #cbd5e1;
        font-size: .98rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: .8rem;
    }

    .panel {
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 16px;
        padding: 1.15rem;
        background: rgba(128,128,128,.045);
        height: 100%;
    }

    .score {
        font-size: 2.7rem;
        font-weight: 850;
        line-height: 1;
    }

    .label {
        font-size: .78rem;
        opacity: .68;
        letter-spacing: .04em;
    }

    .sub {
        font-size: .84rem;
        opacity: .70;
        margin-top: .4rem;
    }

    .status {
        font-size: 1rem;
        font-weight: 750;
        margin-top: .4rem;
    }

    .alert {
        padding: .9rem 1rem;
        border-radius: 12px;
        margin: .45rem 0;
        border: 1px solid rgba(239,68,68,.25);
        background: rgba(239,68,68,.07);
    }

    .success-box {
        padding: .9rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(34,197,94,.25);
        background: rgba(34,197,94,.07);
    }

    .upload-panel {
        padding: 1.25rem;
        border: 1px dashed rgba(100,116,139,.45);
        border-radius: 16px;
        background: rgba(128,128,128,.035);
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 14px;
        padding: .8rem;
        background: rgba(128,128,128,.045);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AGENT LOADING
# ============================================================

@st.cache_resource
def load_agents():
    return {
        "project": ProjectAgent(),
        "resource": ResourceAgent(),
        "weather": WeatherAgent(),
        "safety": SafetyAgent(),
        "site_risk": SiteRiskAgent(),
        "safety_intelligence": SafetyIntelligenceAgent(),
        "compliance": ComplianceAgent(),
        "insurance": InsuranceIntelligenceAgent(),
    }


# ============================================================
# DATASET LOADING
# ============================================================

@st.cache_data
def load_source_data():

    project_df = pd.read_csv(
        "datasets/project_management/project_processed.csv"
    )

    equipment_df = pd.read_csv(
        "datasets/resource/resource_processed.csv"
    )

    weather_df = pd.read_csv(
        "datasets/weather/weather_processed.csv"
    )

    return project_df, equipment_df, weather_df


# ============================================================
# HELPERS
# ============================================================

def run_analysis(
    agents,
    sample_project,
    sample_equipment,
    sample_weather,
    uploaded_image,
):

    image_suffix = Path(
        uploaded_image.name
    ).suffix.lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=image_suffix,
    ) as temporary_file:

        temporary_file.write(
            uploaded_image.getbuffer()
        )

        temporary_image_path = Path(
            temporary_file.name
        )

    try:

        project_risk = agents["project"].predict_risk(
            sample_project
        )

        equipment_mttf = agents["resource"].predict_mttf(
            sample_equipment
        )

        weather_prediction = agents["weather"].predict_weather(
            sample_weather
        )

        safety_report = agents["safety"].inspect_image(
            str(temporary_image_path)
        )

        worker_protection_report = (
            agents["safety_intelligence"]
            .analyze_worker_protection(
                safety_report
            )
        )

        site_report = agents["site_risk"].assess_site(
            project_risk=project_risk,
            equipment_mttf=equipment_mttf,
            weather=weather_prediction,
            safety_report=safety_report,
        )

        compliance_report = (
            agents["compliance"].assess_compliance(
                safety_report=safety_report,
                worker_protection_report=worker_protection_report,
            )
        )

        insurance_report = (
            agents["insurance"].assess_insurance_risk(
                site_report=site_report,
                compliance_report=compliance_report,
                equipment_mttf=equipment_mttf,
            )
        )

        return {
            "project_risk": project_risk,
            "equipment_mttf": equipment_mttf,
            "weather_prediction": weather_prediction,
            "safety_report": safety_report,
            "worker_protection_report": worker_protection_report,
            "site_report": site_report,
            "compliance_report": compliance_report,
            "insurance_report": insurance_report,
            "image_name": uploaded_image.name,
            "image_bytes": uploaded_image.getvalue(),
        }

    finally:

        temporary_image_path.unlink(
            missing_ok=True
        )


# ============================================================
# SESSION STATE
# ============================================================

st.session_state.setdefault(
    "analysis_result",
    None,
)

st.session_state.setdefault(
    "last_saved_inspection_id",
    None,
)


# ============================================================
# LOAD DATA
# ============================================================

agents = load_agents()

project_df, equipment_df, weather_df = (
    load_source_data()
)

project_template = (
    project_df
    .drop(columns=["Risk_Level"])
    .iloc[0]
    .to_dict()
)

equipment_template = (
    equipment_df
    .drop(columns=["MTTF"])
    .iloc[0]
    .to_dict()
)

weather_template = (
    weather_df
    .drop(columns=["Summary"])
    .iloc[0]
    .to_dict()
)

project_types = sorted(
    project_df["Project_Type"]
    .dropna()
    .unique()
)

locations = sorted(
    project_df["Location"]
    .dropna()
    .unique()
)

weather_conditions = sorted(
    project_df["Weather_Condition"]
    .dropna()
    .unique()
)


# ============================================================
# SIDEBAR — PROJECT INPUTS
# ============================================================

with st.sidebar:

    st.markdown("## 🏗️ ConstructAI")

    st.caption(
        "Site Assessment Control Panel"
    )

    st.divider()

    st.markdown(
        "### ⚙️ Project Configuration"
    )

    project_type = st.selectbox(
        "Project Type",
        options=project_types,
        index=project_types.index(
            project_template["Project_Type"]
        ),
    )

    location = st.selectbox(
        "Location",
        options=locations,
        index=locations.index(
            project_template["Location"]
        ),
    )

    weather_condition = st.selectbox(
        "Current Site Weather",
        options=weather_conditions,
        index=weather_conditions.index(
            project_template["Weather_Condition"]
        ),
    )

    planned_cost = st.number_input(
        "Planned Cost",
        min_value=0.0,
        value=float(
            project_template["Planned_Cost"]
        ),
        step=10000.0,
    )

    actual_cost = st.number_input(
        "Current Cost",
        min_value=0.0,
        value=float(
            project_template["Actual_Cost"]
        ),
        step=10000.0,
    )

    accident_count = st.number_input(
        "Recent Accidents",
        min_value=0,
        value=int(
            project_template["Accident_Count"]
        ),
        step=1,
    )

    st.divider()

    st.caption(
        "Configure project conditions here, then upload "
        "a construction-site image in the main workspace."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏗️ Site Assessment</h1>
        <p>
            AI-powered construction site inspection,
            worker protection analysis and risk intelligence.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONTEXT BAR
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Project",
        project_type,
    )

with c2:
    st.metric(
        "Location",
        location,
    )

with c3:
    st.metric(
        "Weather",
        weather_condition,
    )

with c4:
    st.metric(
        "AI Agents",
        "8",
        "Ready",
    )


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📷 Site Image Analysis'
    '</div>',
    unsafe_allow_html=True,
)

upload_left, upload_right = st.columns(
    [1.55, 1],
)

with upload_left:

    st.markdown(
        '<div class="upload-panel">',
        unsafe_allow_html=True,
    )

    st.subheader(
        "Upload Construction-Site Image"
    )

    st.caption(
        "Upload a JPG, JPEG or PNG image containing "
        "workers, PPE, machinery, vehicles or visible "
        "site conditions."
    )

    uploaded_image = st.file_uploader(
        "Choose site image",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="main_image_upload",
        label_visibility="collapsed",
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


with upload_right:

    with st.container(border=True):

        st.subheader(
            "🔬 Analysis Pipeline"
        )

        st.write(
            "ConstructAI will combine:"
        )

        st.write(
            "• Project risk prediction"
        )

        st.write(
            "• Equipment reliability"
        )

        st.write(
            "• Weather intelligence"
        )

        st.write(
            "• Computer vision PPE detection"
        )

        st.write(
            "• Worker protection analysis"
        )

        st.write(
            "• Compliance intelligence"
        )

        st.write(
            "• Insurance risk intelligence"
        )

        analyze_site = st.button(
            "🚀 Analyze Site",
            type="primary",
            use_container_width=True,
        )


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_site:

    if uploaded_image is None:

        st.warning(
            "Upload a construction-site image before "
            "starting the assessment.",
            icon="⚠️",
        )

    else:

        sample_project = (
            project_template.copy()
        )

        sample_project.update(
            {
                "Project_Type": project_type,
                "Location": location,
                "Weather_Condition": weather_condition,
                "Planned_Cost": planned_cost,
                "Actual_Cost": actual_cost,
                "Cost_Overrun": (
                    actual_cost - planned_cost
                ),
                "Accident_Count": accident_count,
            }
        )

        with st.status(
            "Running ConstructAI analysis...",
            expanded=True,
        ) as status:

            st.write(
                "🤖 Project Agent — analyzing project risk"
            )

            st.write(
                "⚙️ Resource Agent — checking equipment reliability"
            )

            st.write(
                "🌦️ Weather Agent — predicting weather risk"
            )

            st.write(
                "🦺 Safety Agent — inspecting PPE and site image"
            )

            st.write(
                "🧠 Safety Intelligence — evaluating worker protection"
            )

            st.write(
                "🏗️ Site Risk Agent — calculating site risk"
            )

            st.write(
                "🛡️ Compliance Agent — checking compliance"
            )

            st.write(
                "🏦 Insurance Agent — calculating insurance risk"
            )

            st.session_state["analysis_result"] = (
                run_analysis(
                    agents=agents,
                    sample_project=sample_project,
                    sample_equipment=(
                        equipment_template.copy()
                    ),
                    sample_weather=(
                        weather_template.copy()
                    ),
                    uploaded_image=uploaded_image,
                )
            )

            result_to_save = (
                st.session_state["analysis_result"]
            )

            inspection_id = save_inspection(
                project_data=sample_project,
                uploaded_image=uploaded_image,
                project_risk=result_to_save[
                    "project_risk"
                ],
                equipment_mttf=result_to_save[
                    "equipment_mttf"
                ],
                weather_prediction=result_to_save[
                    "weather_prediction"
                ],
                safety_report=result_to_save[
                    "safety_report"
                ],
                worker_protection_report=(
                    result_to_save[
                        "worker_protection_report"
                    ]
                ),
                site_report=result_to_save[
                    "site_report"
                ],
                compliance_report=result_to_save[
                    "compliance_report"
                ],
                insurance_report=result_to_save[
                    "insurance_report"
                ],
            )

            st.session_state[
                "last_saved_inspection_id"
            ] = inspection_id

            status.update(
                label=(
                    "Assessment complete • "
                    f"Inspection #{inspection_id} saved"
                ),
                state="complete",
                expanded=False,
            )

        st.toast(
            "Site assessment completed and saved.",
            icon="✅",
        )


# ============================================================
# RESULT
# ============================================================

result = st.session_state[
    "analysis_result"
]


if result is None:

    st.markdown(
        '<div class="section-title">'
        '📋 Assessment Workspace'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.subheader(
            "Ready for a new site assessment"
        )

        st.write(
            "Configure the project details in the sidebar, "
            "upload a site image, and click "
            "**Analyze Site**."
        )

        st.info(
            "Every completed assessment is automatically "
            "saved to the ConstructAI inspection database."
        )

    st.stop()


# ============================================================
# OVERVIEW
# ============================================================

site_report = result["site_report"]
safety_report = result["safety_report"]
protection = result["worker_protection_report"]
compliance = result["compliance_report"]
insurance = result["insurance_report"]


site_score = site_report.get(
    "site_risk_score",
    0,
)

site_level = site_report.get(
    "site_risk_level",
    "Unknown",
)

protection_score = protection.get(
    "safety_score",
    0,
)

protection_level = protection.get(
    "worker_protection_level",
    "Unknown",
)

compliance_score = compliance.get(
    "compliance_score",
    0,
)

compliance_status = compliance.get(
    "compliance_status",
    "Unknown",
)

insurance_score = insurance.get(
    "insurance_risk_score",
    0,
)

insurance_level = insurance.get(
    "insurance_risk_level",
    "Unknown",
)


# ============================================================
# ASSESSMENT SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🎯 Assessment Summary'
    '</div>',
    unsafe_allow_html=True,
)

a, b, c, d = st.columns(4)

with a:

    st.markdown(
        f"""
        <div class="panel">
            <div class="label">SITE RISK</div>
            <div class="score">{int(site_score)}</div>
            <div class="status">{site_level}</div>
            <div class="sub">
                Site-level risk assessment
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        int(site_score)
    )


with b:

    st.markdown(
        f"""
        <div class="panel">
            <div class="label">WORKER PROTECTION</div>
            <div class="score">{int(protection_score)}</div>
            <div class="status">{protection_level}</div>
            <div class="sub">
                Higher score indicates stronger PPE protection
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        int(protection_score)
    )


with c:

    st.markdown(
        f"""
        <div class="panel">
            <div class="label">COMPLIANCE</div>
            <div class="score">{int(compliance_score)}</div>
            <div class="status">{compliance_status}</div>
            <div class="sub">
                Safety compliance assessment
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        int(compliance_score)
    )


with d:

    st.markdown(
        f"""
        <div class="panel">
            <div class="label">INSURANCE RISK</div>
            <div class="score">{int(insurance_score)}</div>
            <div class="status">{insurance_level}</div>
            <div class="sub">
                Internal insurance risk indicator
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        int(insurance_score)
    )


# ============================================================
# SITE RISK
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🏗️ Site Risk Intelligence'
    '</div>',
    unsafe_allow_html=True,
)

left, right = st.columns(
    [1, 1.35]
)

with left:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.subheader(
        "Risk Assessment"
    )

    st.metric(
        "Overall Site Risk",
        site_level,
    )

    st.metric(
        "Risk Score",
        f"{site_score} / 100",
    )

    st.metric(
        "Project Risk",
        result["project_risk"],
    )

    st.metric(
        "Equipment MTTF",
        f"{float(result['equipment_mttf']):.1f}",
    )

    st.metric(
        "Weather Prediction",
        result["weather_prediction"],
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


with right:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.subheader(
        "⚠️ Detected Hazards"
    )

    hazards = site_report.get(
        "hazards",
        [],
    )

    if hazards:

        for hazard in hazards:

            st.warning(
                hazard
            )

    else:

        st.markdown(
            '<div class="success-box">'
            '✅ No site-level hazards identified.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        "### Recommended Actions"
    )

    actions = site_report.get(
        "recommended_actions",
        [],
    )

    if actions:

        for action in actions:

            st.write(
                f"✓ {action}"
            )

    else:

        st.success(
            "Continue standard site monitoring."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SAFETY INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🦺 Safety Intelligence & Worker Protection'
    '</div>',
    unsafe_allow_html=True,
)

image_col, safety_col = st.columns(
    [1.35, 1]
)

with image_col:

    with st.container(border=True):

        st.subheader(
            "📷 Inspected Site Image"
        )

        st.image(
            result["image_bytes"],
            caption=result["image_name"],
            use_container_width=True,
        )


with safety_col:

    with st.container(border=True):

        st.subheader(
            "Worker Protection Status"
        )

        s1, s2 = st.columns(2)

        with s1:

            st.metric(
                "Safety Status",
                safety_report.get(
                    "status",
                    "Unknown",
                ),
            )

        with s2:

            st.metric(
                "Workers Detected",
                protection.get(
                    "workers_detected",
                    0,
                ),
            )

        st.metric(
            "Protection Score",
            f"{protection_score} / 100",
            protection_level,
        )

        violations = protection.get(
            "confirmed_violations",
            [],
        )

        st.markdown(
            "### PPE Findings"
        )

        if violations:

            for violation in violations:

                st.error(
                    violation,
                    icon="⚠️",
                )

        else:

            st.success(
                "No confirmed PPE violations.",
                icon="✅",
            )


# ============================================================
# COMPUTER VISION
# ============================================================

with st.expander(
    "🔍 View Computer Vision Detection Details"
):

    detections = safety_report.get(
        "detections",
        [],
    )

    if detections:

        detection_df = pd.DataFrame(
            detections
        )

        st.dataframe(
            detection_df,
            hide_index=True,
            use_container_width=True,
        )

    else:

        st.info(
            "No trained construction-safety "
            "classes were confidently detected."
        )


# ============================================================
# WORKER ACTIONS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🛠️ Worker Protection Actions'
    '</div>',
    unsafe_allow_html=True,
)

worker_actions = protection.get(
    "recommended_actions",
    [],
)

if worker_actions:

    for index, action in enumerate(
        worker_actions,
        start=1,
    ):

        st.info(
            f"**{index}.** {action}"
        )

else:

    st.success(
        "Continue standard worker-protection monitoring."
    )


# ============================================================
# COMPLIANCE + INSURANCE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🛡️ Compliance & Insurance Intelligence'
    '</div>',
    unsafe_allow_html=True,
)

comp_col, ins_col = st.columns(2)

with comp_col:

    with st.container(border=True):

        st.subheader(
            "Compliance"
        )

        st.metric(
            "Compliance Status",
            compliance_status,
        )

        st.metric(
            "Compliance Score",
            f"{compliance_score} / 100",
        )

        findings = compliance.get(
            "findings",
            [],
        )

        if findings:

            st.markdown(
                "### Findings"
            )

            findings_df = pd.DataFrame(
                findings
            )

            columns = [
                "violation",
                "severity",
                "requirement",
                "action",
            ]

            available = [
                column
                for column in columns
                if column in findings_df.columns
            ]

            st.dataframe(
                findings_df[available],
                hide_index=True,
                use_container_width=True,
            )

        else:

            st.success(
                "No confirmed compliance findings."
            )


with ins_col:

    with st.container(border=True):

        st.subheader(
            "Insurance Risk"
        )

        st.metric(
            "Risk Level",
            insurance_level,
        )

        st.metric(
            "Risk Score",
            f"{insurance_score} / 100",
        )

        st.markdown(
            "### Recommendation"
        )

        st.info(
            insurance.get(
                "recommendation",
                "No recommendation available.",
            )
        )

        if insurance.get("note"):

            st.caption(
                insurance["note"]
            )


# ============================================================
# SAVED RECORD
# ============================================================

if st.session_state[
    "last_saved_inspection_id"
] is not None:

    st.markdown(
        '<div class="section-title">'
        '💾 Inspection Record'
        '</div>',
        unsafe_allow_html=True,
    )

    st.success(
        "This assessment has been saved to the "
        "ConstructAI inspection database."
    )

    st.caption(
        "Inspection ID: "
        f"#{st.session_state['last_saved_inspection_id']}"
    )
