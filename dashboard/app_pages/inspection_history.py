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
# PAGE HEADER
# ============================================================

st.title(":material/history: Inspection history")

st.caption(
    "Review previously saved Construction-AI site assessments, "
    "risk trends, compliance findings, and inspection images."
)


# ============================================================
# HELPER
# ============================================================

def load_json_list(value):
    """Safely convert JSON database text into a Python list."""

    if not value:
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return []


# ============================================================
# LOAD INSPECTIONS
# ============================================================

inspections = get_recent_inspections(
    limit=200
)


# ============================================================
# EMPTY DATABASE
# ============================================================

if not inspections:

    with st.container(border=True):

        st.info(
            "No saved inspections yet. Go to **Site assessment**, "
            "upload a construction-site image, and select "
            "**Analyze site safety**.",
            icon=":material/info:",
        )

    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

inspections_df = pd.DataFrame(
    inspections
)


# Convert timestamp
inspections_df["created_at"] = pd.to_datetime(
    inspections_df["created_at"],
    errors="coerce",
)


# Sort newest first
inspections_df = inspections_df.sort_values(
    "created_at",
    ascending=False,
)


# ============================================================
# OVERVIEW METRICS
# ============================================================

total_inspections = get_inspection_count()


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
        inspections_df["compliance_status"]
        == "Non-Compliant"
    ]
)


st.header(
    ":material/analytics: Inspection overview"
)


with st.container(horizontal=True):

    st.metric(
        "Saved inspections",
        total_inspections,
        border=True,
    )

    st.metric(
        "High-risk inspections",
        high_risk_count,
        border=True,
    )

    st.metric(
        "Unsafe inspections",
        unsafe_count,
        border=True,
    )

    st.metric(
        "Non-compliant inspections",
        non_compliant_count,
        border=True,
    )


# ============================================================
# HISTORICAL ANALYTICS
# ============================================================

st.header(
    ":material/monitoring: Risk analytics"
)


# ------------------------------------------------------------
# Prepare analytics data
# ------------------------------------------------------------

analytics_df = inspections_df.copy()

analytics_df["site_risk_score"] = pd.to_numeric(
    analytics_df["site_risk_score"],
    errors="coerce",
)

analytics_df["safety_score"] = pd.to_numeric(
    analytics_df["safety_score"],
    errors="coerce",
)

analytics_df["insurance_risk_score"] = pd.to_numeric(
    analytics_df["insurance_risk_score"],
    errors="coerce",
)


analytics_df = analytics_df.dropna(
    subset=["created_at"]
)

analytics_df = analytics_df.sort_values(
    "created_at"
)


# ------------------------------------------------------------
# Average metrics
# ------------------------------------------------------------

avg_site_risk = analytics_df[
    "site_risk_score"
].mean()

avg_safety_protection = analytics_df[
    "safety_score"
].mean()

avg_insurance_risk = analytics_df[
    "insurance_risk_score"
].mean()


metric1, metric2, metric3 = st.columns(3)


with metric1:

    if pd.notna(avg_site_risk):

        st.metric(
            "Average site risk",
            f"{avg_site_risk:.1f}/100",
        )

    else:

        st.metric(
            "Average site risk",
            "N/A",
        )


with metric2:

    if pd.notna(avg_safety_protection):

        st.metric(
            "Average safety protection",
            f"{avg_safety_protection:.1f}/100",
        )

    else:

        st.metric(
            "Average safety protection",
            "N/A",
        )


with metric3:

    if pd.notna(avg_insurance_risk):

        st.metric(
            "Average insurance risk",
            f"{avg_insurance_risk:.1f}/100",
        )

    else:

        st.metric(
            "Average insurance risk",
            "N/A",
        )


st.caption(
    "Safety protection score is interpreted as higher-is-better. "
    "Site and insurance scores are risk scores where higher "
    "indicates greater risk."
)


# ============================================================
# RISK TREND
# ============================================================

st.subheader(
    ":material/trending_up: Risk trend"
)


if len(analytics_df) >= 1:

    trend_df = analytics_df[
        [
            "created_at",
            "site_risk_score",
            "insurance_risk_score",
        ]
    ].copy()


    trend_df = trend_df.set_index(
        "created_at"
    )


    trend_df = trend_df.rename(
        columns={
            "site_risk_score": "Site Risk",
            "insurance_risk_score": "Insurance Risk",
        }
    )


    st.line_chart(
        trend_df,
        y=[
            "Site Risk",
            "Insurance Risk",
        ],
        height=320,
    )

else:

    st.info(
        "Not enough data to display risk trends."
    )


# ============================================================
# SAFETY PROTECTION TREND
# ============================================================

st.subheader(
    ":material/health_and_safety: Safety protection trend"
)


if len(analytics_df) >= 1:

    safety_trend_df = analytics_df[
        [
            "created_at",
            "safety_score",
        ]
    ].copy()


    safety_trend_df = safety_trend_df.set_index(
        "created_at"
    )


    safety_trend_df = safety_trend_df.rename(
        columns={
            "safety_score": "Safety Protection Score"
        }
    )


    st.line_chart(
        safety_trend_df,
        y="Safety Protection Score",
        height=280,
    )

else:

    st.info(
        "Not enough data to display safety trends."
    )


# ============================================================
# COMPLIANCE DISTRIBUTION
# ============================================================

st.subheader(
    ":material/gavel: Compliance distribution"
)


compliance_counts = (
    inspections_df[
        "compliance_status"
    ]
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
        height=280,
    )

else:

    st.info(
        "No compliance history is available."
    )


# ============================================================
# FILTERS
# ============================================================

st.header(
    ":material/filter_list: Filter inspections"
)


filter_left, filter_right, filter_third = st.columns(
    3
)


with filter_left:

    risk_filter = st.selectbox(
        "Site-risk level",
        options=[
            "All",
            "Low",
            "Medium",
            "High",
        ],
    )


with filter_right:

    safety_filter = st.selectbox(
        "Safety status",
        options=[
            "All",
            "Safe",
            "Unsafe",
        ],
    )


with filter_third:

    compliance_filter = st.selectbox(
        "Compliance status",
        options=[
            "All",
            "Compliant",
            "Partially Compliant",
            "Non-Compliant",
        ],
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = inspections_df.copy()


if risk_filter != "All":

    filtered_df = filtered_df[
        filtered_df["site_risk_level"]
        == risk_filter
    ]


if safety_filter != "All":

    filtered_df = filtered_df[
        filtered_df["safety_status"]
        == safety_filter
    ]


if compliance_filter != "All":

    filtered_df = filtered_df[
        filtered_df["compliance_status"]
        == compliance_filter
    ]


# ============================================================
# FILTER RESULT
# ============================================================

st.caption(
    f"Showing {len(filtered_df)} inspection(s) "
    f"matching the selected filters."
)


# ============================================================
# INSPECTION TABLE
# ============================================================

st.header(
    ":material/table_chart: Saved inspection records"
)


if filtered_df.empty:

    st.warning(
        "No saved inspections match the selected filters.",
        icon=":material/filter_alt_off:",
    )

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

st.header(
    ":material/visibility: Inspection details"
)


if filtered_df.empty:

    st.info(
        "Select different filters to view an inspection."
    )

    st.stop()


# ============================================================
# INSPECTION SELECTOR
# ============================================================

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
    options=list(
        inspection_options.keys()
    ),
)


selected_id = inspection_options[
    selected_label
]


selected_rows = filtered_df[
    filtered_df["id"] == selected_id
]


if selected_rows.empty:

    st.error(
        "Selected inspection could not be found."
    )

    st.stop()


selected_record = (
    selected_rows.iloc[0]
    .to_dict()
)


# ============================================================
# LOAD SAVED JSON DATA
# ============================================================

selected_hazards = load_json_list(
    selected_record.get(
        "hazards"
    )
)


selected_actions = load_json_list(
    selected_record.get(
        "recommended_actions"
    )
)


selected_violations = load_json_list(
    selected_record.get(
        "ppe_violations"
    )
)


# ============================================================
# DETAILS
# ============================================================

detail_left, detail_right = st.columns(
    [1.1, 1]
)


# ------------------------------------------------------------
# Saved image
# ------------------------------------------------------------

with detail_left:

    with st.container(border=True):

        st.subheader(
            "Saved inspection image"
        )


        image_path_value = selected_record.get(
            "image_path"
        )


        if image_path_value:

            image_path = Path(
                image_path_value
            )


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
                    "The saved inspection image file "
                    "could not be found.",
                    icon=":material/image_not_supported:",
                )

        else:

            st.warning(
                "No image path was saved for this inspection."
            )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

with detail_right:

    with st.container(border=True):

        st.subheader(
            "Risk and compliance summary"
        )


        st.metric(
            "Overall site risk",
            selected_record.get(
                "site_risk_level",
                "Unknown",
            ),
        )


        st.metric(
            "Site-risk score",
            f"{selected_record.get('site_risk_score', 0)} / 100",
        )


        st.metric(
            "Safety status",
            selected_record.get(
                "safety_status",
                "Unknown",
            ),
        )


        st.metric(
            "Safety protection score",
            f"{selected_record.get('safety_score', 0)} / 100",
        )


        st.metric(
            "Compliance status",
            selected_record.get(
                "compliance_status",
                "Unknown",
            ),
        )


        st.metric(
            "Insurance risk",
            selected_record.get(
                "insurance_risk_level",
                "Unknown",
            ),
        )


        equipment_value = selected_record.get(
            "equipment_mttf",
            0,
        )


        try:

            equipment_value = float(
                equipment_value
            )

            equipment_text = (
                f"{equipment_value:.1f}"
            )

        except (
            TypeError,
            ValueError,
        ):

            equipment_text = "N/A"


        st.metric(
            "Equipment MTTF",
            equipment_text,
        )


        st.write(
            f"**Weather:** "
            f"{selected_record.get('weather_prediction', 'Unknown')}"
        )


# ============================================================
# HAZARDS & PPE
# ============================================================

hazards_column, violations_column = st.columns(
    2
)


with hazards_column:

    with st.container(border=True):

        st.subheader(
            "Detected hazards"
        )


        if selected_hazards:

            for hazard in selected_hazards:

                st.warning(
                    hazard,
                    icon=":material/warning:",
                )

        else:

            st.success(
                "No saved hazards for this inspection."
            )


with violations_column:

    with st.container(border=True):

        st.subheader(
            "Confirmed PPE violations"
        )


        if selected_violations:

            for violation in selected_violations:

                st.error(
                    violation,
                    icon=":material/report:",
                )

        else:

            st.success(
                "No confirmed PPE violations."
            )


# ============================================================
# RECOMMENDED ACTIONS
# ============================================================

with st.container(border=True):

    st.subheader(
        "Recommended actions"
    )


    if selected_actions:

        for index, action in enumerate(
            selected_actions,
            start=1,
        ):

            st.write(
                f":material/check_circle: "
                f"**{index}.** {action}"
            )

    else:

        st.success(
            "No actions were recorded for this inspection."
        )


# ============================================================
# INSPECTION INFORMATION
# ============================================================

with st.container(border=True):

    st.subheader(
        "Inspection information"
    )


    info_col1, info_col2, info_col3 = st.columns(
        3
    )


    with info_col1:

        st.write(
            f"**Inspection ID:** "
            f"#{selected_record.get('id', 'N/A')}"
        )

        st.write(
            f"**Project type:** "
            f"{selected_record.get('project_type', 'N/A')}"
        )


    with info_col2:

        st.write(
            f"**Location:** "
            f"{selected_record.get('location', 'N/A')}"
        )

        st.write(
            f"**Project risk:** "
            f"{selected_record.get('project_risk', 'N/A')}"
        )


    with info_col3:

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

st.divider()

st.header(
    ":material/notifications_active: Live Monitoring Alert History"
)

st.caption(
    "Alerts automatically generated by the real-time "
    "construction-site camera monitoring system."
)

try:

    live_alerts = get_recent_live_alerts(
        limit=50
    )

except Exception as e:

    st.error(
        f"Unable to load live monitoring alerts: {e}"
    )

    live_alerts = []


if live_alerts:

    # --------------------------------------------------------
    # ALERT METRICS
    # --------------------------------------------------------

    total_live_alerts = len(
        live_alerts
    )

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


    metric1, metric2, metric3 = st.columns(3)


    with metric1:

        st.metric(
            "Total live alerts",
            total_live_alerts,
            border=True,
        )


    with metric2:

        st.metric(
            "Critical alerts",
            critical_alerts,
            border=True,
        )


    with metric3:

        st.metric(
            "Warning alerts",
            warning_alerts,
            border=True,
        )


    # --------------------------------------------------------
    # ALERT TABLE
    # --------------------------------------------------------

    st.subheader(
        ":material/table_chart: Recent live alerts"
    )

    live_alert_df = pd.DataFrame(
        live_alerts
    )


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
            "worker_protection_level":
                "Worker protection",
            "workers_detected":
                "Workers",
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

            "Date and time":
                st.column_config.DatetimeColumn(
                    "Date and time",
                    format="DD MMM YYYY, HH:mm:ss",
                ),

            "Risk score":
                st.column_config.ProgressColumn(
                    "Risk score",
                    min_value=0,
                    max_value=100,
                    format="%d / 100",
                ),

            "Safety score":
                st.column_config.ProgressColumn(
                    "Safety score",
                    min_value=0,
                    max_value=100,
                    format="%d / 100",
                ),
        },
    )


    # --------------------------------------------------------
    # ALERT DETAILS
    # --------------------------------------------------------

    st.subheader(
        ":material/visibility: Live alert details"
    )


    alert_options = {}

    for alert in live_alerts:

        alert_id = alert.get(
            "id"
        )

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
        options=list(
            alert_options.keys()
        ),
    )


    selected_alert_id = alert_options[
        selected_alert_label
    ]


    selected_alert = next(
        (
            alert
            for alert in live_alerts
            if alert.get("id")
            == selected_alert_id
        ),
        None,
    )


    if selected_alert:

        st.markdown("---")


        detail_col1, detail_col2 = st.columns(
            2
        )


        # ----------------------------------------------------
        # BASIC ALERT INFORMATION
        # ----------------------------------------------------

        with detail_col1:

            with st.container(
                border=True
            ):

                st.subheader(
                    "Alert information"
                )

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


        # ----------------------------------------------------
        # RISK INFORMATION
        # ----------------------------------------------------

        with detail_col2:

            with st.container(
                border=True
            ):

                st.subheader(
                    "Risk information"
                )

                st.metric(
                    "Site risk",
                    selected_alert.get(
                        "site_risk_level",
                        "Unknown",
                    ),
                )

                st.metric(
                    "Site-risk score",
                    f"{selected_alert.get('site_risk_score', 0)} / 100",
                )

                st.metric(
                    "Safety score",
                    f"{selected_alert.get('safety_score', 0)} / 100",
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
        # PPE VIOLATIONS
        # ----------------------------------------------------

        st.subheader(
            ":material/health_and_safety: PPE violations"
        )

        selected_violations = load_json_list(
            selected_alert.get(
                "ppe_violations"
            )
        )


        if selected_violations:

            for violation in selected_violations:

                st.error(
                    violation,
                    icon=":material/report:",
                )

        else:

            st.success(
                "No PPE violations recorded."
            )


        # ----------------------------------------------------
        # HAZARDS
        # ----------------------------------------------------

        st.subheader(
            ":material/warning: Detected hazards"
        )

        selected_live_hazards = load_json_list(
            selected_alert.get(
                "hazards"
            )
        )


        if selected_live_hazards:

            for hazard in selected_live_hazards:

                st.warning(
                    hazard,
                    icon=":material/warning:",
                )

        else:

            st.info(
                "No hazards recorded for this alert."
            )


        # ----------------------------------------------------
        # RECOMMENDED ACTIONS
        # ----------------------------------------------------

        st.subheader(
            ":material/check_circle: Recommended actions"
        )

        selected_live_actions = load_json_list(
            selected_alert.get(
                "recommended_actions"
            )
        )


        if selected_live_actions:

            for index, action in enumerate(
                selected_live_actions,
                start=1,
            ):

                st.write(
                    f":material/check_circle: "
                    f"**{index}.** {action}"
                )

        else:

            st.info(
                "No recommended actions recorded."
            )


else:

    st.info(
        "No live monitoring alerts have been recorded yet.",
        icon=":material/info:",
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