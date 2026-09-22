from pathlib import Path
import json
import sqlite3
from uuid import uuid4


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_DIRECTORY = PROJECT_ROOT / "database"

DATABASE_PATH = DATABASE_DIRECTORY / "construction_ai.db"

IMAGE_DIRECTORY = DATABASE_DIRECTORY / "inspection_images"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a SQLite connection with named columns enabled.
    """

    DATABASE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Create all required database tables if they do not exist.
    """

    IMAGE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = get_connection()

    # ========================================================
    # INSPECTIONS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            project_type TEXT,
            location TEXT,
            image_filename TEXT,
            image_path TEXT,

            project_risk TEXT,
            equipment_mttf REAL,
            weather_prediction TEXT,

            site_risk_level TEXT,
            site_risk_score INTEGER,

            safety_status TEXT,
            safety_score INTEGER,
            workers_detected INTEGER,
            ppe_violations TEXT,

            compliance_status TEXT,
            compliance_score INTEGER,

            insurance_risk_level TEXT,
            insurance_risk_score INTEGER,

            hazards TEXT,
            recommended_actions TEXT
        )
        """
    )

    # ========================================================
    # INSPECTION INDEX
    # ========================================================

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS index_inspections_created_at
        ON inspections(created_at DESC)
        """
    )

    # ========================================================
    # LIVE ALERTS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS live_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            alert_level TEXT NOT NULL,
            alert_message TEXT NOT NULL,

            site_risk_level TEXT,
            site_risk_score INTEGER,

            safety_score INTEGER,
            worker_protection_level TEXT,
            workers_detected INTEGER,

            ppe_violations TEXT,
            hazards TEXT,
            recommended_actions TEXT
        )
        """
    )

    # ========================================================
    # USERS TABLE
    # ========================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            username TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'Worker',

            is_verified INTEGER NOT NULL DEFAULT 1,

            created_at TEXT NOT NULL,

            last_login TEXT
        )
        """
    )

    # ========================================================
    # COMMIT CHANGES
    # ========================================================

    connection.commit()

    connection.close()


# ============================================================
# SAVE SITE INSPECTION
# ============================================================

def save_inspection(
    project_data,
    uploaded_image,
    project_risk,
    equipment_mttf,
    weather_prediction,
    safety_report,
    worker_protection_report,
    site_report,
    compliance_report,
    insurance_report,
):
    """
    Save a completed site assessment and its uploaded image.

    Returns:
        Newly created inspection ID.
    """

    initialize_database()

    # --------------------------------------------------------
    # Save uploaded image
    # --------------------------------------------------------

    original_filename = uploaded_image.name

    file_extension = Path(
        original_filename
    ).suffix.lower()

    saved_image_name = (
        f"inspection_{uuid4().hex}"
        f"{file_extension}"
    )

    saved_image_path = (
        IMAGE_DIRECTORY / saved_image_name
    )

    saved_image_path.write_bytes(
        uploaded_image.getvalue()
    )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO inspections (
            project_type,
            location,
            image_filename,
            image_path,

            project_risk,
            equipment_mttf,
            weather_prediction,

            site_risk_level,
            site_risk_score,

            safety_status,
            safety_score,
            workers_detected,
            ppe_violations,

            compliance_status,
            compliance_score,

            insurance_risk_level,
            insurance_risk_score,

            hazards,
            recommended_actions
        )
        VALUES (
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?,
            ?, ?,
            ?, ?,
            ?, ?
        )
        """,
        (
            project_data["Project_Type"],
            project_data["Location"],
            original_filename,
            str(saved_image_path),

            project_risk,
            float(equipment_mttf),
            weather_prediction,

            site_report["site_risk_level"],
            int(site_report["site_risk_score"]),

            safety_report["status"],
            int(
                worker_protection_report[
                    "safety_score"
                ]
            ),
            int(
                worker_protection_report[
                    "workers_detected"
                ]
            ),
            json.dumps(
                worker_protection_report[
                    "confirmed_violations"
                ]
            ),

            compliance_report[
                "compliance_status"
            ],
            int(
                compliance_report[
                    "compliance_score"
                ]
            ),

            insurance_report[
                "insurance_risk_level"
            ],
            int(
                insurance_report[
                    "insurance_risk_score"
                ]
            ),

            json.dumps(
                site_report["hazards"]
            ),

            json.dumps(
                site_report[
                    "recommended_actions"
                ]
            ),
        ),
    )

    inspection_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return inspection_id


# ============================================================
# SAVE LIVE ALERT
# ============================================================

def save_live_alert(
    alert,
    site_risk_level,
    site_risk_score,
    safety_score,
    worker_protection_level,
    workers_detected,
    violations,
    hazards,
    recommended_actions,
):
    """
    Save a real-time AI safety alert generated
    by live monitoring.

    Returns:
        Newly created alert ID.
    """

    initialize_database()

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO live_alerts (
            alert_level,
            alert_message,

            site_risk_level,
            site_risk_score,

            safety_score,
            worker_protection_level,
            workers_detected,

            ppe_violations,
            hazards,
            recommended_actions
        )
        VALUES (
            ?, ?,
            ?, ?,
            ?, ?, ?,
            ?, ?, ?
        )
        """,
        (
            alert.get(
                "level",
                "WARNING",
            ),

            alert.get(
                "message",
                "Construction site alert detected.",
            ),

            site_risk_level,
            int(site_risk_score),

            int(safety_score),
            worker_protection_level,
            int(workers_detected),

            json.dumps(violations),

            json.dumps(hazards),

            json.dumps(
                recommended_actions
            ),
        ),
    )

    alert_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return alert_id


# ============================================================
# GET RECENT INSPECTIONS
# ============================================================

def get_recent_inspections(
    limit=20,
):
    """
    Return the newest inspection records first.
    """

    initialize_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM inspections
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET INSPECTION COUNT
# ============================================================

def get_inspection_count():
    """
    Return the total number of saved inspections.
    """

    initialize_database()

    connection = get_connection()

    row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM inspections
        """
    ).fetchone()

    connection.close()

    return row["total"]


# ============================================================
# GET RECENT LIVE ALERTS
# ============================================================

def get_recent_live_alerts(
    limit=50,
):
    """
    Return the newest live monitoring alerts first.
    """

    initialize_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM live_alerts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]