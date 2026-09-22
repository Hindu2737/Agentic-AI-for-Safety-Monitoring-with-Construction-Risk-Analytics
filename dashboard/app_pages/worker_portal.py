import streamlit as st


st.title("👷 Worker Safety Portal")

st.caption(
    "Safety information, PPE status, and important site instructions."
)


# ============================================================
# USER INFORMATION
# ============================================================

username = st.session_state.get("username", "Worker")

st.success(f"Welcome, {username}!")


# ============================================================
# PPE STATUS
# ============================================================

st.subheader("🦺 PPE Safety")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Hardhat", "Required")

with col2:
    st.metric("Safety Vest", "Required")

with col3:
    st.metric("Mask", "Where Applicable")


# ============================================================
# SAFETY INSTRUCTION
# ============================================================

st.subheader("⚠️ Safety Instructions")

st.warning(
    "Wear all required PPE before entering or continuing work "
    "on the construction site."
)


# ============================================================
# SITE SAFETY RULES
# ============================================================

st.subheader("📋 Site Safety Rules")

rules = [
    "Wear the required hardhat at all times.",
    "Wear a high-visibility safety vest.",
    "Use the required mask where applicable.",
    "Follow instructions from the site safety officer.",
    "Report unsafe conditions immediately.",
    "Do not continue work when a serious safety hazard is identified.",
]

for rule in rules:
    st.markdown(f"- {rule}")


# ============================================================
# IMPORTANT NOTICE
# ============================================================

st.subheader("📢 Important")

st.info(
    "If you notice an unsafe condition or PPE issue, "
    "inform the site safety officer immediately."
)