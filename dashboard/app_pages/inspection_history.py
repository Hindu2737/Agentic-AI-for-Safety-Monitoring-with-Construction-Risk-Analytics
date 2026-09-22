import json
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.database import (
    get_inspection_count,
    get_recent_inspections,
    get_recent_live_alerts,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ConstructAI | Inspection History",
    page_icon="📋",
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

    .record-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        min-height: 108px;
        box-shadow: 0 2px 10px rgba(0,0,0,.04);
    }

    .record-label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: .7px;
        font-weight: 700;
    }

    .record-value {
        font-size: 25px;
        font-weight: 800;
        margin-top: 8px;
        color: #111827;
    }

    .record-meta {
        font-size: 12px;
        color: #6b7280;
        margin-top: 5px;
    }

    .danger-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #fecaca;
        background: #fef2f2;
    }

    .safe-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #bbf7d0;
        background: #f0fdf4;
    }

    .info-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #dbeafe;
        background: #eff6ff;
    }

    .muted {
        color: #6b7280;
        font-size: 12px;
    }

    .section-divider {
        margin: 28px 0 10px 0;
        border-top: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-brand">CONSTRUCTAI • RISK INTELLIGENCE PLATFORM</div>
        <div class="hero-title">Inspection & Alert History</div>
        <div class="hero-subtitle">
            Centralized records for site assessments, safety findings,
            compliance, risk trends and real-time monitoring alerts.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def load_json_list(value):
    """Safely convert JSON database text into a Python list."""
    if not value:
        return []

    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# LOAD DATA
# ============================================================

inspections = get_recent_inspections(limit=200)
total_inspections = get_inspection_count()


# ============================================================
# EMPTY DATABASE
# ============================================================

if not inspections:
    st.markdown(
        """
        <div class="info-card">
            <b>No saved inspections yet.</b><br>
            <span class="muted">
                Run a Site Assessment first. Once an assessment is saved,
                its risk, safety, compliance and image information will appear
                here.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

inspections_df = pd.DataFrame(inspections)

inspections_df["created_at"] = pd.to_datetime(
    inspections_df["created_at"],
    errors="coerce",
)

inspections_df = inspections_df.sort_values(
    "created_at",
    ascending=False,
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

high_risk_count = len(
    inspections_df[
        inspections_df["site_risk_level"] == "High"
    ]
)

unsafe_count = len(
    inspections_df[
        inspections_df["safety_status"] == "Unsafe"
    ]
)

non_compliant_count = len(
    inspections_df[
        inspections_df["compliance_status"] == "Non-Compliant"
    ]
)

st.markdown(
    '<div class="section-title">Records overview</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="record-card">
            <div class="record-label">Saved inspections</div>
            <div class="record-value">{total_inspections}</div>
            <div class="record-meta">Historical site assessments</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="record-card">
            <div class="record-label">High-risk records</div>
            <div class="record-value">{high_risk_count}</div>
            <div class="record-meta">Site risk classified High</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="record-card">
            <div class="record-label">Unsafe inspections</div>
            <div class="record-value">{unsafe_count}</div>
            <div class="record-meta">Safety status marked Unsafe</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
        <div class="record-card">
            <div class="record-label">Non-compliant</div>
            <div class="record-value">{non_compliant_count}</div>
            <div class="record-meta">Compliance status requiring action</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HISTORICAL ANALYTICS
# ============================================================

st.markdown(
    '<div class="section-title">Historical risk intelligence</div>',
    unsafe_allow_html=True,
)

analytics_df = inspections_df.copy()

for column in [
    "site_risk_score",
    "safety_score",
    "insurance_risk_score",
]:
    analytics_df[column] = pd.to_numeric(
        analytics_df[column],
        errors="coerce",
    )

analytics_df = analytics_df.dropna(subset=["created_at"])
analytics_df = analytics_df.sort_values("created_at")

avg_site_risk = analytics_df["site_risk_score"].mean()
avg_safety = analytics_df["safety_score"].mean()
avg_insurance = analytics_df["insurance_risk_score"].mean()

a1, a2, a3 = st.columns(3)

with a1:
    st.metric(
        "Average site risk",
        f"{avg_site_risk:.1f}/100"
        if pd.notna(avg_site_risk)
        else "N/A",
    )

with a2:
    st.metric(
        "Average safety protection",
        f"{avg_safety:.1f}/100"
        if pd.notna(avg_safety)
        else "N/A",
    )

with a3:
    st.metric(
        "Average insurance risk",
        f"{avg_insurance:.1f}/100"
        if pd.notna(avg_insurance)
        else "N/A",
    )

st.caption(
    "Safety protection is higher-is-better. Site and insurance scores "
    "represent risk, where higher values indicate greater risk."
)


# ============================================================
# TRENDS
# ============================================================

trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    st.markdown(
        '<div class="section-title">Site & insurance risk trend</div>',
        unsafe_allow_html=True,
    )

    if len(analytics_df) >= 1:
        trend_df = analytics_df[
            [
                "created_at",
                "site_risk_score",
                "insurance_risk_score",
            ]
        ].copy()

        trend_df = trend_df.set_index("created_at")
        trend_df = trend_df.rename(
            columns={
                "site_risk_score": "Site Risk",
                "insurance_risk_score": "Insurance Risk",
            }
        )

        st.line_chart(
            trend_df,
            y=["Site Risk", "Insurance Risk"],
            height=300,
        )
    else:
        st.info("Not enough data to display risk trends.")

with trend_col2:
    st.markdown(
        '<div class="section-title">Safety protection trend</div>',
        unsafe_allow_html=True,
    )

    if len(analytics_df) >= 1:
        safety_trend_df = analytics_df[
            [
                "created_at",
                "safety_score",
            ]
        ].copy()

        safety_trend_df = safety_trend_df.set_index("created_at")
        safety_trend_df = safety_trend_df.rename(
            columns={
                "safety_score": "Safety Protection Score"
            }
        )

        st.line_chart(
            safety_trend_df,
            y="Safety Protection Score",
            height=300,
        )
    else:
        st.info("Not enough data to display safety trends.")


# ============================================================
# COMPLIANCE DISTRIBUTION
# ============================================================

st.markdown(
    '<div class="section-title">Compliance distribution</div>',
    unsafe_allow_html=True,
)

compliance_counts = (
    inspections_df["compliance_status"]
    .value_counts()
)

if not compliance_counts.empty:
    compliance_chart = (
        compliance_counts
        .rename_axis("Compliance Status")
        .to_frame("Inspections")
    )

    st.bar_chart(
        compliance_chart,
        y="Inspections",
        height=260,
    )
else:
    st.info("No compliance history is available.")


# ============================================================
# FILTERS
# ============================================================

st.markdown(
    '<div class="section-title">Find an inspection record</div>',
    unsafe_allow_html=True,
)

f1, f2, f3 = st.columns(3)

with f1:
    risk_filter = st.selectbox(
        "Site-risk level",
        ["All", "Low", "Medium", "High"],
    )

with f2:
    safety_filter = st.selectbox(
        "Safety status",
        ["All", "Safe", "Unsafe"],
    )

with f3:
    compliance_filter = st.selectbox(
        "Compliance status",
        [
            "All",
            "Compliant",
            "Partially Compliant",
            "Non-Compliant",
        ],
    )

filtered_df = inspections_df.copy()

if risk_filter != "All":
    filtered_df = filtered_df[
        filtered_df["site_risk_level"] == risk_filter
    ]

if safety_filter != "All":
    filtered_df = filtered_df[
        filtered_df["safety_status"] == safety_filter
    ]

if compliance_filter != "All":
    filtered_df = filtered_df[
        filtered_df["compliance_status"] == compliance_filter
    ]

st.caption(
    f"Showing {len(filtered_df)} inspection(s) matching the selected filters."
)


# ============================================================
# INSPECTION RECORD TABLE
# ============================================================

st.markdown(
    '<div class="section-title">Saved inspection records</div>',
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.warning("No saved inspections match the selected filters.")
else:
    display_df = filtered_df[
        [
            "id",
            "created_at",
            "project_type",
            "location",
            "site_risk_level",
            "site_risk_score",
            "safety_status",
            "compliance_status",
            "insurance_risk_level",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "id": "Inspection ID",
            "created_at": "Date and time",
            "project_type": "Project type",
            "location": "Location",
            "site_risk_level": "Site risk",
            "site_risk_score": "Risk score",
            "safety_status": "Safety status",
            "compliance_status": "Compliance status",
            "insurance_risk_level": "Insurance risk",
        }
    )

    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Risk score": st.column_config.ProgressColumn(
                "Risk score",
                min_value=0,
                max_value=100,
                format="%d / 100",
            ),
            "Date and time": st.column_config.DatetimeColumn(
                "Date and time",
                format="DD MMM YYYY, HH:mm",
            ),
        },
    )


# ============================================================
# INSPECTION DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">Inspection intelligence record</div>',
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.info("Select different filters to view an inspection.")
else:

    inspection_options = {}

    for _, row in filtered_df.iterrows():
        created_at = row["created_at"]

        if pd.notna(created_at):
            date_text = created_at.strftime(
                "%d %b %Y, %H:%M"
            )
        else:
            date_text = "Unknown date"

        label = (
            f"#{row['id']} • "
            f"{row['project_type']} • "
            f"{row['location']} • "
            f"{date_text}"
        )

        inspection_options[label] = row["id"]

    selected_label = st.selectbox(
        "Select a saved inspection",
        options=list(inspection_options.keys()),
    )

    selected_id = inspection_options[selected_label]

    selected_rows = filtered_df[
        filtered_df["id"] == selected_id
    ]

    if selected_rows.empty:
        st.error("Selected inspection could not be found.")
        st.stop()

    selected_record = (
        selected_rows.iloc[0]
        .to_dict()
    )

    selected_hazards = load_json_list(
        selected_record.get("hazards")
    )

    selected_actions = load_json_list(
        selected_record.get("recommended_actions")
    )

    selected_violations = load_json_list(
        selected_record.get("ppe_violations")
    )


    # ========================================================
    # RECORD HEADER
    # ========================================================

    selected_risk = selected_record.get(
        "site_risk_level",
        "Unknown",
    )

    selected_safety = selected_record.get(
        "safety_status",
        "Unknown",
    )

    selected_compliance = selected_record.get(
        "compliance_status",
        "Unknown",
    )

    selected_insurance = selected_record.get(
        "insurance_risk_level",
        "Unknown",
    )

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric("Site Risk", selected_risk)

    with r2:
        st.metric(
            "Risk Score",
            f"{safe_float(selected_record.get('site_risk_score')):.0f}/100",
        )

    with r3:
        st.metric("Safety", selected_safety)

    with r4:
        st.metric("Compliance", selected_compliance)


    # ========================================================
    # IMAGE + INTELLIGENCE
    # ========================================================

    detail_left, detail_right = st.columns(
        [1.15, 1]
    )

    with detail_left:
        st.markdown(
            '<div class="section-title">Inspection evidence</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):

            image_path_value = selected_record.get(
                "image_path"
            )

            if image_path_value:
                image_path = Path(image_path_value)

                if image_path.exists():
                    st.image(
                        str(image_path),
                        caption=selected_record.get(
                            "image_filename",
                            "Inspection image",
                        ),
                        width="stretch",
                    )
                else:
                    st.warning(
                        "The saved inspection image file could not be found."
                    )
            else:
                st.warning(
                    "No image path was saved for this inspection."
                )

    with detail_right:
        st.markdown(
            '<div class="section-title">Assessment summary</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):

            st.metric(
                "Safety protection score",
                f"{safe_float(selected_record.get('safety_score')):.0f}/100",
            )

            equipment_value = safe_float(
                selected_record.get("equipment_mttf"),
                0,
            )

            st.metric(
                "Equipment MTTF",
                f"{equipment_value:.1f}",
            )

            st.metric(
                "Insurance risk",
                selected_insurance,
            )

            st.write(
                f"**Weather:** "
                f"{selected_record.get('weather_prediction', 'Unknown')}"
            )

            st.write(
                f"**Project risk:** "
                f"{selected_record.get('project_risk', 'Unknown')}"
            )

            st.write(
                f"**Workers detected:** "
                f"{selected_record.get('workers_detected', 0)}"
            )


    # ========================================================
    # HAZARDS + PPE
    # ========================================================

    h1, h2 = st.columns(2)

    with h1:
        st.markdown(
            '<div class="section-title">Detected hazards</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            if selected_hazards:
                for hazard in selected_hazards:
                    st.warning(hazard)
            else:
                st.success(
                    "No saved hazards for this inspection."
                )

    with h2:
        st.markdown(
            '<div class="section-title">Confirmed PPE violations</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            if selected_violations:
                for violation in selected_violations:
                    st.error(violation)
            else:
                st.success(
                    "No confirmed PPE violations."
                )


    # ========================================================
    # ACTION PLAN
    # ========================================================

    st.markdown(
        '<div class="section-title">Corrective action plan</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        if selected_actions:
            for index, action in enumerate(
                selected_actions,
                start=1,
            ):
                st.write(
                    f"**{index}.** {action}"
                )
        else:
            st.success(
                "No corrective actions were recorded."
            )


    # ========================================================
    # RECORD INFORMATION
    # ========================================================

    st.markdown(
        '<div class="section-title">Inspection metadata</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        m1, m2, m3 = st.columns(3)

        with m1:
            st.write(
                f"**Inspection ID:** "
                f"#{selected_record.get('id', 'N/A')}"
            )
            st.write(
                f"**Project type:** "
                f"{selected_record.get('project_type', 'N/A')}"
            )

        with m2:
            st.write(
                f"**Location:** "
                f"{selected_record.get('location', 'N/A')}"
            )
            st.write(
                f"**Project risk:** "
                f"{selected_record.get('project_risk', 'N/A')}"
            )

        with m3:
            st.write(
                f"**Workers detected:** "
                f"{selected_record.get('workers_detected', 0)}"
            )
            st.write(
                f"**Insurance score:** "
                f"{selected_record.get('insurance_risk_score', 0)} / 100"
            )


# ============================================================
# LIVE MONITORING ALERT HISTORY
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Live monitoring alert history</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Automatic alerts generated by the real-time construction-site "
    "camera monitoring system."
)

try:
    live_alerts = get_recent_live_alerts(limit=50)
except Exception as e:
    st.error(f"Unable to load live monitoring alerts: {e}")
    live_alerts = []


if live_alerts:

    total_live_alerts = len(live_alerts)

    critical_alerts = sum(
        1
        for alert in live_alerts
        if alert.get("alert_level") == "CRITICAL"
    )

    warning_alerts = sum(
        1
        for alert in live_alerts
        if alert.get("alert_level") == "WARNING"
    )

    la1, la2, la3 = st.columns(3)

    with la1:
        st.metric(
            "Total live alerts",
            total_live_alerts,
        )

    with la2:
        st.metric(
            "Critical alerts",
            critical_alerts,
        )

    with la3:
        st.metric(
            "Warning alerts",
            warning_alerts,
        )


    # ========================================================
    # ALERT TABLE
    # ========================================================

    live_alert_df = pd.DataFrame(live_alerts)

    display_alert_df = live_alert_df[
        [
            "id",
            "created_at",
            "alert_level",
            "alert_message",
            "site_risk_level",
            "site_risk_score",
            "safety_score",
            "worker_protection_level",
            "workers_detected",
        ]
    ].copy()

    display_alert_df = display_alert_df.rename(
        columns={
            "id": "Alert ID",
            "created_at": "Date and time",
            "alert_level": "Alert level",
            "alert_message": "Message",
            "site_risk_level": "Site risk",
            "site_risk_score": "Risk score",
            "safety_score": "Safety score",
            "worker_protection_level": "Worker protection",
            "workers_detected": "Workers",
        }
    )

    display_alert_df["Date and time"] = pd.to_datetime(
        display_alert_df["Date and time"],
        errors="coerce",
    )

    st.dataframe(
        display_alert_df,
        hide_index=True,
        width="stretch",
        column_config={
            "Date and time": st.column_config.DatetimeColumn(
                "Date and time",
                format="DD MMM YYYY, HH:mm:ss",
            ),
            "Risk score": st.column_config.ProgressColumn(
                "Risk score",
                min_value=0,
                max_value=100,
                format="%d / 100",
            ),
            "Safety score": st.column_config.ProgressColumn(
                "Safety score",
                min_value=0,
                max_value=100,
                format="%d / 100",
            ),
        },
    )


    # ========================================================
    # ALERT DETAILS
    # ========================================================

    st.markdown(
        '<div class="section-title">Live alert intelligence</div>',
        unsafe_allow_html=True,
    )

    alert_options = {}

    for alert in live_alerts:
        alert_id = alert.get("id")
        created_at = alert.get(
            "created_at",
            "Unknown time",
        )
        level = alert.get(
            "alert_level",
            "WARNING",
        )

        alert_options[
            f"#{alert_id} • {level} • {created_at}"
        ] = alert_id

    selected_alert_label = st.selectbox(
        "Select a live alert",
        options=list(alert_options.keys()),
    )

    selected_alert_id = alert_options[
        selected_alert_label
    ]

    selected_alert = next(
        (
            alert
            for alert in live_alerts
            if alert.get("id") == selected_alert_id
        ),
        None,
    )

    if selected_alert:

        alert_level = selected_alert.get(
            "alert_level",
            "WARNING",
        )

        if alert_level == "CRITICAL":
            st.error(
                f"🚨 CRITICAL ALERT — "
                f"{selected_alert.get('alert_message', 'No message')}"
            )
        else:
            st.warning(
                f"⚠️ WARNING — "
                f"{selected_alert.get('alert_message', 'No message')}"
            )

        ac1, ac2 = st.columns(2)

        with ac1:
            with st.container(border=True):
                st.subheader("Alert information")

                st.write(
                    f"**Alert ID:** "
                    f"#{selected_alert.get('id', 'N/A')}"
                )

                st.write(
                    f"**Date and time:** "
                    f"{selected_alert.get('created_at', 'N/A')}"
                )

                st.write(
                    f"**Alert level:** "
                    f"{selected_alert.get('alert_level', 'N/A')}"
                )

                st.write(
                    f"**Message:** "
                    f"{selected_alert.get('alert_message', 'N/A')}"
                )

        with ac2:
            with st.container(border=True):
                st.subheader("Risk information")

                st.metric(
                    "Site risk",
                    selected_alert.get(
                        "site_risk_level",
                        "Unknown",
                    ),
                )

                st.metric(
                    "Site-risk score",
                    f"{safe_float(selected_alert.get('site_risk_score')):.0f}/100",
                )

                st.metric(
                    "Safety score",
                    f"{safe_float(selected_alert.get('safety_score')):.0f}/100",
                )

                st.write(
                    f"**Worker protection:** "
                    f"{selected_alert.get('worker_protection_level', 'Unknown')}"
                )

                st.write(
                    f"**Workers detected:** "
                    f"{selected_alert.get('workers_detected', 0)}"
                )


        # ----------------------------------------------------
        # PPE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">PPE violations</div>',
            unsafe_allow_html=True,
        )

        selected_live_violations = load_json_list(
            selected_alert.get("ppe_violations")
        )

        if selected_live_violations:
            for violation in selected_live_violations:
                st.error(violation)
        else:
            st.success(
                "No PPE violations recorded."
            )


        # ----------------------------------------------------
        # HAZARDS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Detected hazards</div>',
            unsafe_allow_html=True,
        )

        selected_live_hazards = load_json_list(
            selected_alert.get("hazards")
        )

        if selected_live_hazards:
            for hazard in selected_live_hazards:
                st.warning(hazard)
        else:
            st.info(
                "No hazards recorded for this alert."
            )


        # ----------------------------------------------------
        # ACTIONS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Recommended actions</div>',
            unsafe_allow_html=True,
        )

        selected_live_actions = load_json_list(
            selected_alert.get("recommended_actions")
        )

        if selected_live_actions:
            for index, action in enumerate(
                selected_live_actions,
                start=1,
            ):
                st.write(
                    f"**{index}.** {action}"
                )
        else:
            st.info(
                "No recommended actions recorded."
            )

else:
    st.markdown(
        """
        <div class="safe-card">
            <b>No live monitoring alerts have been recorded yet.</b><br>
            <span class="muted">
                Start Live Monitoring to generate real-time safety alerts.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# REFRESH
# ============================================================

st.markdown("---")

if st.button(
    "🔄 Refresh inspection history",
    use_container_width=True,
):
    st.rerun()
