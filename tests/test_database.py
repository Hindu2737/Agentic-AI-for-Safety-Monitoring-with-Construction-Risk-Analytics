from utils.database import (
    initialize_database,
    get_inspection_count,
    get_recent_inspections,
    get_recent_live_alerts,
)


def test_database_initializes():
    initialize_database()

    count = get_inspection_count()

    assert isinstance(count, int)
    assert count >= 0


def test_recent_inspections_returns_list():
    inspections = get_recent_inspections(limit=5)

    assert isinstance(inspections, list)


def test_recent_live_alerts_returns_list():
    alerts = get_recent_live_alerts(limit=5)

    assert isinstance(alerts, list)