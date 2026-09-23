import streamlit as st
from main import run_analysis
from reporting.risk_summary import create_risk_summary
from reporting.recommendations import generate_recommendations
from reporting.pdf_generator import generate_pdf_report

st.set_page_config(
    page_title="ConstructAI | Executive Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Professional UI ----------
st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.5rem;padding-bottom:3rem}
.hero{padding:1.7rem 2rem;border-radius:18px;background:linear-gradient(135deg,#0f172a,#1e293b);color:white;margin-bottom:1rem}
.hero h1{margin:0;font-size:2.25rem;font-weight:800}
.hero p{margin:.35rem 0 0;color:#cbd5e1}
.section{font-size:1.35rem;font-weight:750;margin:1.5rem 0 .8rem}
.card{border:1px solid rgba(128,128,128,.20);border-radius:16px;padding:1.1rem;background:rgba(128,128,128,.045);height:100%}
.big{font-size:3rem;font-weight:850;line-height:1}
.label{font-size:.82rem;opacity:.68}
.sub{font-size:.85rem;opacity:.72;margin-top:.35rem}
.alert{border-radius:12px;padding:.8rem 1rem;margin:.45rem 0;border:1px solid rgba(239,68,68,.25);background:rgba(239,68,68,.07)}
.ok{border-radius:12px;padding:.9rem 1rem;border:1px solid rgba(34,197,94,.25);background:rgba(34,197,94,.07)}
.agent{padding:.65rem .8rem;border-bottom:1px solid rgba(128,128,128,.15)}
</style>
""", unsafe_allow_html=True)

if "dashboard_analysis_result" not in st.session_state:
    st.session_state["dashboard_analysis_result"] = None

# ---------- Header ----------
st.markdown("""
<div class="hero">
<h1>🏗️ ConstructAI</h1>
<p>Agentic AI-Based Construction Risk Intelligence and Safety Monitoring Platform</p>
</div>
""", unsafe_allow_html=True)

h1, h2, h3 = st.columns([5,2,2])
with h1:
    st.caption("AI-powered project, safety, compliance and operational intelligence")
with h2:
    st.metric("AI Agents", "8 / 8", "Active")
with h3:
    st.metric("System", "Operational")

@st.cache_data(ttl=300)
def get_analysis_results():
    return run_analysis()

try:
    if st.session_state["dashboard_analysis_result"] is None:
        with st.spinner("Running Construction-AI intelligence agents..."):
            results = get_analysis_results()
        st.session_state["dashboard_analysis_result"] = results
    else:
        results = st.session_state["dashboard_analysis_result"]
except Exception as e:
    st.error("Unable to run the Construction-AI analysis pipeline.")
    st.exception(e)
    st.stop()

if not isinstance(results, dict):
    st.error("The analysis pipeline did not return a valid result.")
    st.stop()

try:
    summary = create_risk_summary(results)
except Exception as e:
    st.error("Unable to create the risk summary.")
    st.exception(e)
    st.stop()

project_risk = results.get("project_risk", "Unknown")
equipment_mttf = results.get("equipment_mttf", 0)
weather = results.get("weather_prediction", results.get("weather", "Unknown"))
safety = results.get("safety_report", {})
protection = results.get("worker_protection_report", {})
site = results.get("site_report", {})
compliance = results.get("compliance_report", {})
insurance = results.get("insurance_report", {})

def number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

site_score = max(0, min(100, number(site.get("site_risk_score"))))
protection_score = max(0, min(100, number(protection.get("safety_score"), 100)))
safety_risk = 100 - protection_score
insurance_score = max(0, min(100, number(insurance.get("insurance_risk_score"))))
compliance_score = number(compliance.get("compliance_score"))
overall = round((site_score + safety_risk + insurance_score) / 3)

if overall >= 70:
    overall_level = "High"
elif overall >= 40:
    overall_level = "Medium"
else:
    overall_level = "Low"

violations = protection.get("confirmed_violations", [])
hazards = site.get("hazards", [])
workers = protection.get("workers_detected", 0)
compliance_status = compliance.get("compliance_status", "Unknown")
insurance_level = insurance.get("insurance_risk_level", "Unknown")

# ---------- Executive risk ----------
st.markdown('<div class="section">🎯 Executive Risk Overview</div>', unsafe_allow_html=True)

a,b,c = st.columns([1.2,1,1])
with a:
    st.markdown(f"""
    <div class="card">
    <div class="label">OVERALL SITE RISK</div>
    <div class="big">{overall}<span style="font-size:1.1rem">/100</span></div>
    <div><b>{overall_level} Risk</b></div>
    <div class="sub">Combined site, worker-safety and insurance risk indicators</div>
    </div>""", unsafe_allow_html=True)
    st.progress(overall)

with b:
    st.markdown(f"""
    <div class="card">
    <div class="label">PROJECT RISK</div>
    <div class="big">{project_risk}</div>
    <div class="sub">Predicted by Project Agent</div>
    </div>""", unsafe_allow_html=True)

with c:
    st.markdown(f"""
    <div class="card">
    <div class="label">WORKER PROTECTION</div>
    <div class="big">{int(protection_score)}<span style="font-size:1.1rem">/100</span></div>
    <div><b>{protection.get("worker_protection_level","Unknown")}</b></div>
    <div class="sub">{workers} worker(s) detected • {len(violations)} confirmed PPE violation(s)</div>
    </div>""", unsafe_allow_html=True)
    st.progress(int(protection_score))

# ---------- KPI strip ----------
st.markdown('<div class="section">📊 Operational Intelligence</div>', unsafe_allow_html=True)
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("🏗️ Site Risk", f"{int(site_score)}/100", site.get("site_risk_level","Unknown"))
k2.metric("🦺 Safety Risk", f"{int(safety_risk)}/100")
k3.metric("🛡️ Compliance", f"{int(compliance_score)}/100", compliance_status)
k4.metric("🏦 Insurance", f"{int(insurance_score)}/100", insurance_level)
k5.metric("⚙️ Equipment MTTF", f"{number(equipment_mttf):.1f}")

# ---------- Risk distribution ----------
st.markdown('<div class="section">📈 Risk Distribution</div>', unsafe_allow_html=True)
chart_data = {
    "Site Risk": int(site_score),
    "Safety Risk": int(safety_risk),
    "Insurance Risk": int(insurance_score),
}
st.bar_chart(chart_data, horizontal=True, height=230)

# ---------- Attention ----------
alerts = []
if str(project_risk).lower() == "high":
    alerts.append("🔴 High project risk detected.")
elif str(project_risk).lower() == "medium":
    alerts.append("🟠 Medium project risk detected.")
if site_score >= 60:
    alerts.append("🔴 Site risk is high. Additional inspection is recommended.")
elif site_score >= 30:
    alerts.append("🟠 Site risk requires attention.")
for v in violations:
    alerts.append(f"🔴 PPE violation detected: {v}")
if weather in {"Rain","Light Rain","Heavy Rain","Windy","Overcast"}:
    alerts.append(f"🟠 Weather-related risk detected: {weather}")
if number(equipment_mttf) < 100:
    alerts.append("🔴 Equipment may fail soon. Immediate inspection recommended.")
elif number(equipment_mttf) < 300:
    alerts.append("🟠 Equipment maintenance should be scheduled.")
if compliance_status != "Compliant":
    alerts.append(f"🔴 Compliance status: {compliance_status}")
if insurance_level == "High":
    alerts.append("🔴 High insurance risk indicator detected.")

st.markdown('<div class="section">🚨 Critical Attention</div>', unsafe_allow_html=True)
if alerts:
    for alert in alerts:
        st.markdown(f'<div class="alert">{alert}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="ok">✅ No major risk alerts detected.</div>', unsafe_allow_html=True)

# ---------- Safety ----------
st.markdown('<div class="section">🦺 Site Safety Intelligence</div>', unsafe_allow_html=True)
s1,s2,s3 = st.columns(3)
s1.metric("Workers Detected", workers)
s2.metric("PPE Violations", len(violations))
s3.metric("Protection Score", f"{int(protection_score)}/100")

d1,d2 = st.columns(2)
with d1:
    st.markdown("#### Computer Vision Detections")
    detections = safety.get("detections", [])
    if detections:
        for item in detections:
            label = item.get("label","Unknown")
            confidence = number(item.get("confidence")) * 100
            st.write(f"**{label}** — {confidence:.1f}% confidence")
    else:
        st.success("No detections recorded.")
with d2:
    st.markdown("#### PPE Findings")
    if violations:
        for v in violations:
            st.error(v)
    else:
        st.success("No confirmed PPE violations.")

# ---------- Hazards/actions ----------
st.markdown('<div class="section">⚠️ Site Hazards & Corrective Actions</div>', unsafe_allow_html=True)
hcol, acol = st.columns(2)
with hcol:
    st.markdown("#### Identified Hazards")
    if hazards:
        for h in hazards:
            st.warning(h)
    else:
        st.success("No site hazards identified.")
with acol:
    st.markdown("#### Recommended Actions")
    actions = []
    actions.extend(site.get("recommended_actions", []))
    actions.extend(protection.get("recommended_actions", []))
    actions.extend(compliance.get("recommended_actions", []))
    if insurance.get("recommendation"):
        actions.append(insurance["recommendation"])
    actions = list(dict.fromkeys(actions))
    if actions:
        for i, action in enumerate(actions, 1):
            st.info(f"**{i}.** {action}")
    else:
        st.success("Continue routine monitoring and preventive controls.")

# ---------- Compliance / insurance ----------
st.markdown('<div class="section">🛡️ Compliance & Insurance Intelligence</div>', unsafe_allow_html=True)
cc, ic = st.columns(2)
with cc:
    st.markdown("#### Compliance")
    st.metric("Compliance Score", f"{int(compliance_score)}/100", compliance_status)
    findings = compliance.get("findings", [])
    if findings:
        for f in findings:
            with st.container(border=True):
                st.markdown(f"**{f.get('violation','Unknown')}**")
                st.caption(f"Severity: {f.get('severity','Unknown')}")
                st.write(f"Requirement: {f.get('requirement','')}")
                st.write(f"Action: {f.get('action','')}")
    else:
        st.success("No compliance findings.")
with ic:
    st.markdown("#### Insurance Risk")
    st.metric("Insurance Risk", f"{int(insurance_score)}/100", insurance_level)
    st.info(insurance.get("recommendation","No recommendation available."))
    if insurance.get("note"):
        st.caption(insurance["note"])

# ---------- Agent network ----------
st.markdown('<div class="section">🤖 AI Agent Network</div>', unsafe_allow_html=True)
agents = [
    ("Project Agent","Project risk prediction"),
    ("Resource Agent","Equipment reliability / MTTF"),
    ("Weather Agent","Weather risk prediction"),
    ("Safety Agent","Computer vision PPE detection"),
    ("Safety Intelligence Agent","Worker protection intelligence"),
    ("Site Risk Agent","Site-level risk assessment"),
    ("Compliance Agent","Safety compliance assessment"),
    ("Insurance Intelligence Agent","Insurance risk intelligence"),
]
for name, desc in agents:
    x,y,z = st.columns([2.2,5.5,1])
    x.markdown(f"**{name}**")
    y.caption(desc)
    z.success("Active")

# ---------- Reporting ----------
st.markdown('<div class="section">📄 Reporting Intelligence</div>', unsafe_allow_html=True)
if st.button("📄 Generate Risk Report", use_container_width=True):
    with st.spinner("Generating Construction-AI risk report..."):
        try:
            recommendations = generate_recommendations(results)
            pdf_file = generate_pdf_report(
                summary=summary,
                results=results,
                recommendations=recommendations,
            )
            st.success("✅ Risk report generated successfully.")
            st.download_button(
                "⬇️ Download Risk Report",
                data=pdf_file.getvalue(),
                file_name="ConstructAI_Risk_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error("❌ Unable to generate the risk report.")
            st.exception(e)

# ---------- Detailed output ----------
with st.expander("🔎 Detailed Agent Output"):
    tabs = st.tabs([
        "Project","Resource","Weather","Safety",
        "Worker Protection","Site Risk","Compliance","Insurance"
    ])
    outputs = [
        {"project_risk": project_risk},
        {"equipment_mttf": equipment_mttf},
        {"weather_prediction": weather},
        safety,
        protection,
        site,
        compliance,
        insurance,
    ]
    for tab, output in zip(tabs, outputs):
        with tab:
            st.json(output)

# ---------- Refresh ----------
st.markdown("---")
if st.button("🔄 Refresh Analysis", use_container_width=True):
    st.cache_data.clear()
    st.session_state["dashboard_analysis_result"] = None
    st.rerun()
