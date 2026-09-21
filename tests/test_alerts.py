from utils.alerts import AlertManager


def test_high_site_risk_creates_critical_alert():
    manager = AlertManager(cooldown_seconds=0)

    alert = manager.check_alert(
        site_risk_level="High",
        site_risk_score=80,
        worker_protection_level="Good",
        safety_score=100,
        violations=[],
    )

    assert alert is not None
    assert alert["level"] == "CRITICAL"


def test_ppe_violation_creates_warning():
    manager = AlertManager(cooldown_seconds=0)

    alert = manager.check_alert(
        site_risk_level="Low",
        site_risk_score=10,
        worker_protection_level="Needs Attention",
        safety_score=50,
        violations=["NO-Hardhat"],
    )

    assert alert is not None
    assert alert["level"] == "WARNING"
    assert "NO-Hardhat" in alert["message"]


def test_no_risk_returns_no_alert():
    manager = AlertManager(cooldown_seconds=0)

    alert = manager.check_alert(
        site_risk_level="Low",
        site_risk_score=10,
        worker_protection_level="Good",
        safety_score=100,
        violations=[],
    )

    assert alert is None