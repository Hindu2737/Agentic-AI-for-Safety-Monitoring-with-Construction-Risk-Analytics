import time


class AlertManager:

    def __init__(self, cooldown_seconds=10):
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = 0
        self.last_alert_key = None

    def check_alert(
        self,
        site_risk_level,
        site_risk_score,
        worker_protection_level,
        safety_score,
        violations,
    ):

        # ----------------------------------------------------
        # Determine whether an alert is required
        # ----------------------------------------------------

        alert_level = None
        alert_message = None

        # HIGH SITE RISK
        if site_risk_level == "High":

            alert_level = "CRITICAL"

            alert_message = (
                f"High site risk detected "
                f"({site_risk_score}/100). "
                f"Immediate corrective action is recommended."
            )

        # CRITICAL WORKER PROTECTION
        elif worker_protection_level == "Critical":

            alert_level = "CRITICAL"

            alert_message = (
                "Critical worker protection condition detected. "
                "Immediate PPE compliance is required."
            )

        # PPE VIOLATION
        elif violations:

            alert_level = "WARNING"

            violation_text = ", ".join(
                violations
            )

            alert_message = (
                f"PPE violation detected: "
                f"{violation_text}. "
                f"Corrective action is required."
            )

        # NO ALERT
        else:

            return None

        # ----------------------------------------------------
        # Prevent alert spam
        # ----------------------------------------------------

        alert_key = (
            alert_level,
            alert_message,
        )

        current_time = time.time()

        if (
            self.last_alert_key == alert_key
            and
            current_time - self.last_alert_time
            < self.cooldown_seconds
        ):

            return None

        # ----------------------------------------------------
        # Store alert state
        # ----------------------------------------------------

        self.last_alert_time = current_time
        self.last_alert_key = alert_key

        return {
            "level": alert_level,
            "message": alert_message,
            "timestamp": current_time,
        }