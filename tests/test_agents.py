from agents.project_agent import ProjectAgent
from agents.resource_agent import ResourceAgent
from agents.weather_agent import WeatherAgent
from agents.safety_intelligence_agent import SafetyIntelligenceAgent
from agents.site_risk_agent import SiteRiskAgent
from agents.safety_agent import SafetyAgent
from agents.compliance_agent import ComplianceAgent
from agents.insurance_agent import InsuranceIntelligenceAgent


def test_project_agent_loads():
    agent = ProjectAgent()
    assert agent.model is not None


def test_resource_agent_loads():
    agent = ResourceAgent()
    assert agent.model is not None


def test_weather_agent_loads():
    agent = WeatherAgent()
    assert agent.model is not None


def test_safety_intelligence_agent():
    agent = SafetyIntelligenceAgent()

    safety_report = {
        "status": "Unsafe",
        "detections": [
            {
                "label": "Person",
                "confidence": 0.95,
            },
            {
                "label": "NO-Hardhat",
                "confidence": 0.90,
            },
        ],
        "violations": [
            {
                "label": "NO-Hardhat",
                "confidence": 0.90,
            }
        ],
    }

    result = agent.analyze_worker_protection(safety_report)

    assert result["safety_score"] == 75
    assert result["worker_protection_level"] == "Needs Attention"
    assert "NO-Hardhat" in result["confirmed_violations"]


def test_site_risk_agent():
    agent = SiteRiskAgent()

    safety_report = {
        "status": "Unsafe",
        "violations": [
            {
                "label": "NO-Hardhat",
                "confidence": 0.90,
            }
        ],
    }

    result = agent.assess_site(
        project_risk="High",
        equipment_mttf=50,
        weather="Rain",
        safety_report=safety_report,
    )

    assert result["site_risk_score"] == 100
    assert result["site_risk_level"] == "High"
    assert len(result["hazards"]) > 0

def test_safety_agent_loads():
    agent = SafetyAgent()
    assert agent is not None


def test_compliance_agent():
    agent = ComplianceAgent()

    safety_report = {
        "detections": [
            {
                "label": "Person",
                "confidence": 0.95,
            },
            {
                "label": "NO-Hardhat",
                "confidence": 0.90,
            },
        ]
    }

    worker_protection_report = {
        "confirmed_violations": ["NO-Hardhat"]
    }

    result = agent.assess_compliance(
        safety_report,
        worker_protection_report,
    )

    assert result["compliance_status"] == "Partially Compliant"
    assert result["compliance_score"] == 65
    assert len(result["findings"]) == 1


def test_insurance_intelligence_agent():
    agent = InsuranceIntelligenceAgent()

    site_report = {
        "site_risk_score": 40
    }

    compliance_report = {
        "compliance_status": "Non-Compliant"
    }

    result = agent.assess_insurance_risk(
        site_report,
        compliance_report,
        equipment_mttf=50,
    )

    assert result["insurance_risk_score"] == 80
    assert result["insurance_risk_level"] == "High"
    assert "recommendation" in result