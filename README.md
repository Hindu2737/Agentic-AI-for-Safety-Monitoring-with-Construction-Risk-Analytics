# 🏗️ Safety Monitoring with Construction Risk Analytics

## Agentic Construction Risk Intelligence Platform

Construction-AI is an AI-powered construction risk intelligence platform designed to identify, analyze, and communicate risks across construction projects.

The platform combines machine learning, computer vision, specialized AI agents, site-risk intelligence, worker-safety analysis, compliance monitoring, equipment reliability prediction, automated alerts, database persistence, and automated reporting into a unified application.

---

## 🎯 Project Objective

Construction projects involve multiple interconnected risks, including:

- Project delays
- Cost overruns
- Equipment failures
- Unsafe weather conditions
- Worker PPE violations
- Site hazards
- Safety compliance issues
- Operational and insurance-related risks

Construction-AI brings these risk factors together and uses specialized AI agents to provide a consolidated view of construction-site risk.

---

# 🚀 Key Features

## 🤖 Multi-Agent Risk Intelligence

The platform uses multiple specialized AI agents:

1. **Project Agent**
   - Predicts project-level risk.

2. **Resource Agent**
   - Predicts equipment Mean Time To Failure (MTTF).

3. **Weather Agent**
   - Predicts weather conditions relevant to construction operations.

4. **Safety / YOLO Agent**
   - Uses computer vision to detect workers and PPE violations from construction-site images and live camera frames.

5. **Safety Intelligence Agent**
   - Converts PPE detections into worker-protection intelligence and recommended actions.

6. **Site Risk Agent**
   - Combines project, equipment, weather, and safety information to calculate overall site risk.

7. **Compliance Agent**
   - Evaluates PPE-related compliance and identifies compliance findings.

8. **Insurance Intelligence Agent**
   - Produces an internal insurance-risk indicator based on site risk, compliance, and equipment reliability.

---

# 🦺 Computer Vision Safety Monitoring

Construction-AI uses YOLO-based object detection to analyze construction-site images and live camera frames.

The system can identify:

- Workers
- Missing hardhats
- Missing masks
- Missing safety vests

Detected violations are passed to the Safety Intelligence Agent for further analysis.

## Safety Intelligence

The platform converts detected PPE violations into:

- Worker protection level
- Safety score
- Confirmed violations
- Recommended corrective actions
- Number of workers detected

---

# 📊 Site Risk Monitoring

The Site Risk Agent combines outputs from multiple agents.

Risk factors include:

- Project risk
- Equipment reliability
- Weather conditions
- PPE violations

The system produces:

- Site risk level
- Site risk score
- Identified hazards
- Recommended actions

Risk levels are classified as:

- **Low**
- **Medium**
- **High**

---

# 🛡️ Compliance Intelligence

The Compliance Agent evaluates detected PPE violations against defined safety requirements.

It provides:

- Compliance status
- Compliance score
- Violation details
- Severity
- Required actions

Compliance levels include:

- **Compliant**
- **Partially Compliant**
- **Non-Compliant**

---

# 🏢 Insurance Risk Intelligence

The Insurance Intelligence Agent generates an internal risk-support indicator using:

- Site risk
- Compliance status
- Equipment reliability

The result includes:

- Insurance risk level
- Insurance risk score
- Risk recommendation

> **Note:** The insurance indicator is an internal risk-support metric. It is not an insurance quote, policy decision, legal determination, or professional insurance assessment.

---

# 🖥️ Application Dashboard

Construction-AI provides a Streamlit-based web application.

The application contains four main pages:

- Site Assessment
- Executive Dashboard
- Live Monitoring
- Inspection History

---

## 🦺 Site Assessment

Users can:

- Enter project information
- Provide equipment information
- Provide weather information
- Upload construction-site images
- Run the AI analysis pipeline
- View safety and risk results
- View compliance intelligence
- View insurance intelligence
- Save completed inspections
- Generate and download risk reports

---

## 📊 Executive Dashboard

The Executive Dashboard provides a consolidated view of:

- Overall risk
- Project risk
- Site risk
- Worker safety risk
- Weather
- Equipment MTTF
- Compliance
- Insurance risk
- Active alerts
- Site hazards
- Recommended actions
- Agent status
- Safety detections

The dashboard also provides risk breakdowns and operational intelligence from the integrated AI agents.

---

## 📹 Live Monitoring

Construction-AI provides real-time construction-site monitoring using a browser camera and YOLO-based computer vision.

The Live Monitoring page provides:

- Real-time worker detection
- PPE violation detection
- Worker protection analysis
- Safety score
- Site risk score
- Site risk level
- Detected hazards
- Recommended corrective actions
- Automatic safety alerts

The monitoring pipeline continuously analyzes camera frames and passes detected safety violations through the Safety Intelligence and Site Risk agents.

### Live Monitoring Pipeline

```text
Browser Camera
      │
      ▼
Streamlit WebRTC
      │
      ▼
Safety / YOLO Agent
      │
      ▼
Safety Intelligence Agent
      │
      ▼
Site Risk Agent
      │
      ├──────────────► Automatic Alert
      │                       │
      │                       ├──► Email Notification
      │                       │
      │                       └──► SQLite Database
      │
      ▼
Live Monitoring Dashboard
      │
      ▼
Inspection History
```

---

## 🚨 Automatic Safety Alerts

The platform generates automatic alerts when significant safety conditions are detected.

Alert conditions include:

- High site risk
- Critical worker protection conditions
- PPE violations

Alerts include:

- Alert level
- Alert message
- Site risk information
- Safety information
- Detected PPE violations
- Recommended corrective actions

A cooldown mechanism is used to prevent repeated alerts for the same condition.

---

## 📧 Email Notifications

Construction-AI can automatically send safety alerts through email using the Resend API.

Email alerts contain:

- Alert level
- Safety alert message
- Automatic notification information

Email configuration is stored using environment variables and should not be committed to GitHub.

---

## 🚨 Live Alert History

Live monitoring alerts are stored in the SQLite database.

Users can review previous live alerts through the Inspection History page.

Stored information includes:

- Alert timestamp
- Alert level
- Alert message
- Site risk level
- Site risk score
- Safety score
- Worker protection level
- Workers detected
- PPE violations
- Hazards
- Recommended actions

---

## 📜 Inspection History

The platform stores completed inspections in SQLite.

Users can review:

- Previous inspections
- Inspection date and time
- Project type
- Location
- Site risk
- Safety status
- Compliance status
- Insurance risk
- Equipment MTTF
- Saved inspection images
- Detected hazards
- PPE violations
- Recommended actions

Historical analytics include:

- Average site risk
- Average safety protection score
- Average insurance risk
- Site and insurance risk trends
- Safety protection trends
- Compliance distribution

The Inspection History page also provides access to stored live monitoring alerts.

---

# 📄 Automated Risk Reporting

Construction-AI generates an automated PDF Risk Intelligence Report.

The report contains:

- Executive summary
- Overall risk
- Risk breakdown
- Worker safety intelligence
- PPE violations
- Site hazards
- Equipment intelligence
- Weather intelligence
- Compliance intelligence
- Insurance intelligence
- Recommended actions

Users can generate and download the report directly from the application.

---

# 🧠 System Architecture

```text
                         ┌─────────────────────────┐
                         │      Streamlit UI       │
                         │                         │
                         │  Site Assessment        │
                         │  Executive Dashboard    │
                         │  Live Monitoring         │
                         │  Inspection History     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Analysis Pipeline    │
                         │        main.py          │
                         └────────────┬────────────┘
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
               ▼                      ▼                      ▼
        Project Agent          Resource Agent          Weather Agent
               │                      │                      │
               └──────────────────────┼──────────────────────┘
                                      │
                                      ▼
                            Safety / YOLO Agent
                                      │
                                      ▼
                         Safety Intelligence Agent
                                      │
                                      ▼
                              Site Risk Agent
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                 Compliance Agent       Insurance Intelligence
                         │                         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                              Risk Intelligence
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
             Dashboard          SQLite Database        PDF Report
```

---

# 📹 Live Monitoring Architecture

```text
Browser Camera
      │
      ▼
Streamlit WebRTC
      │
      ▼
Safety / YOLO Agent
      │
      ▼
Safety Intelligence Agent
      │
      ▼
Site Risk Agent
      │
      ├──────────────► Automatic Alert
      │                       │
      │                       ├──► Email
      │                       │
      │                       └──► SQLite
      │
      ▼
Live Monitoring Dashboard
      │
      ▼
Inspection History
```

---

# 🧪 Automated Testing

The project uses `pytest` for automated testing.

The test suite covers:

- AI agent initialization and behavior
- Safety intelligence
- Site risk assessment
- Compliance intelligence
- Insurance intelligence
- Alert generation
- Database operations
- Live alert history

## Run all tests

```bash
python -m pytest tests -v
```

Current automated test suite:

```text
14 tests passed
```

Test structure:

```text
tests/
├── test_agents.py
├── test_alerts.py
└── test_database.py
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Hindu2737/Agentic-AI-for-Safety-Monitoring-with-Construction-Risk-Analytics.git
```

Move into the project directory:

```bash
cd Agentic-AI-for-Safety-Monitoring-with-Construction-Risk-Analytics
```

---

## 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
RESEND_API_KEY=your_resend_api_key
ALERT_EMAIL_TO=your_email@example.com
ALERT_EMAIL_FROM=onboarding@resend.dev
```

### Important

Do not commit `.env` to GitHub.

The `.gitignore` file should contain:

```text
.env
```

---

# ▶️ Running the Application

Start the Streamlit application:

```powershell
streamlit run dashboard/app.py
```

The application provides:

```text
Site Assessment
Executive Dashboard
Live Monitoring
Inspection History
```

---

# 🗄️ Database

Construction-AI uses SQLite for persistent application data.

Database location:

```text
database/construction_ai.db
```

The database stores:

- Completed inspections
- Inspection metadata
- Saved inspection images
- Risk information
- Safety information
- Compliance information
- Insurance information
- Live monitoring alerts

Inspection images are stored under:

```text
database/inspection_images/
```

---

# 🤖 Machine Learning Models

The platform uses trained machine learning pipelines and YOLO-based computer vision.

Model files are stored under:

```text
models/
```

The project also contains the YOLO model used for safety detection.

The main trained model components include:

```text
models/
├── project_risk_pipeline.pkl
├── resource_mttf_pipeline.pkl
└── weather_summary_pipeline.pkl
```

The Safety / YOLO Agent uses the trained YOLO weights located under the project's `runs/` directory.

---

# 📁 Project Structure

```text
Construction-AI/
│
├── agents/
│   ├── compliance_agent.py
│   ├── insurance_agent.py
│   ├── project_agent.py
│   ├── resource_agent.py
│   ├── safety_agent.py
│   ├── safety_intelligence_agent.py
│   ├── site_risk_agent.py
│   └── weather_agent.py
│
├── dashboard/
│   ├── app.py
│   └── app_pages/
│       ├── site_assessment.py
│       ├── dashboard.py
│       ├── live_monitoring.py
│       └── inspection_history.py
│
├── database/
│   ├── construction_ai.db
│   └── inspection_images/
│
├── datasets/
│
├── docs/
│
├── models/
│   ├── project_risk_pipeline.pkl
│   ├── resource_mttf_pipeline.pkl
│   └── weather_summary_pipeline.pkl
│
├── notebooks/
│
├── preprocessing/
│
├── reporting/
│
├── runs/
│
├── tests/
│   ├── test_agents.py
│   ├── test_alerts.py
│   └── test_database.py
│
├── training/
│
├── utils/
│   ├── alerts.py
│   ├── database.py
│   └── email_alerts.py
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── yolov8n.pt
```

---

# 🛠️ Technology Stack

### Programming

- Python

### Machine Learning

- Scikit-learn
- Joblib
- NumPy
- Pandas

### Computer Vision

- YOLO
- Ultralytics
- OpenCV
- PyTorch
- Torchvision
- Pillow

### Frontend / Application

- Streamlit
- Streamlit WebRTC

### Database

- SQLite

### Reporting

- ReportLab

### Notifications

- Resend
- Python Dotenv

### Testing

- Pytest

### Version Control

- Git
- GitHub

---

# 🔄 End-to-End Workflow

The complete Construction-AI workflow is:

```text
Construction Project Data
          │
          ▼
   ┌───────────────┐
   │ Project Agent │
   └───────┬───────┘
           │
           ▼
   Project Risk Prediction
           │
           ├──────────────────────┐
           ▼                      ▼
   Resource Agent           Weather Agent
           │                      │
           ▼                      ▼
   Equipment MTTF          Weather Prediction
           │                      │
           └──────────┬───────────┘
                      ▼
               Safety / YOLO
                      │
                      ▼
              PPE Detection
                      │
                      ▼
        Safety Intelligence Agent
                      │
                      ▼
            Worker Protection
                      │
                      ▼
               Site Risk Agent
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 Compliance Agent      Insurance Intelligence
          │                       │
          └───────────┬───────────┘
                      ▼
              Risk Intelligence
                      │
       ┌──────────────┼───────────────┐
       ▼              ▼               ▼
   Dashboard       Database        PDF Report
                      │
                      ▼
              Inspection History
```

---

# 🚨 Real-Time Alert Workflow

```text
Live Camera
     │
     ▼
YOLO Detection
     │
     ▼
PPE Violation
     │
     ▼
Safety Intelligence
     │
     ▼
Site Risk Assessment
     │
     ▼
Alert Manager
     │
     ├──────────────► Email Notification
     │
     └──────────────► SQLite Live Alert
                              │
                              ▼
                       Inspection History
```

---

# 🔒 Security Notes

Sensitive configuration should be stored in environment variables.

Do not commit:

```text
.env
```

API keys, credentials, and other secrets should not be placed directly inside Python source files.

---

# 📌 Current Project Status

The current application includes:

- ✅ Multi-agent construction risk intelligence
- ✅ Project risk prediction
- ✅ Equipment reliability prediction
- ✅ Weather prediction
- ✅ YOLO-based PPE detection
- ✅ Worker protection intelligence
- ✅ Site risk monitoring
- ✅ Compliance intelligence
- ✅ Insurance risk intelligence
- ✅ Streamlit frontend
- ✅ Executive dashboard
- ✅ Real-time camera monitoring
- ✅ Automatic safety alerts
- ✅ Email notifications
- ✅ SQLite persistence
- ✅ Live alert history
- ✅ Inspection history
- ✅ PDF risk reporting
- ✅ Automated testing
- ✅ GitHub version control

---

# 🚀 Future Enhancements

Potential future enhancements include:

- SMS notifications
- IoT sensor integration
- CCTV / RTSP camera integration
- Cloud deployment
- Docker containerization
- CI/CD automation
- Additional construction quality monitoring
- Expanded compliance rule sets
- Additional predictive maintenance capabilities

---

# 📜 License

This project is distributed under the license included in the repository.

See:

```text
LICENSE
```

---

# 👥 Project

**Construction-AI — Agentic Construction Risk Intelligence Platform**

An AI-powered platform for construction risk monitoring, worker safety intelligence, automated alerts, compliance analysis, and operational risk reporting.
