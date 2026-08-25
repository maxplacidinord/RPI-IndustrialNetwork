from fastapi.testclient import TestClient

from drive_monitor.api import create_app
from drive_monitor.config import AppConfig


def test_simulator_api_is_read_only() -> None:
    config = AppConfig.model_validate(
        {
            "provider": "simulator",
            "poll_interval_seconds": 0.2,
            "drives": [{"id": "test-drive", "model": "SK500P", "nodes": []}],
        }
    )
    with TestClient(create_app(config)) as client:
        response = client.get("/api/v1/drives")
        assert response.status_code == 200
        assert response.json()["drives"][0]["drive_id"] == "test-drive"
        assert client.post("/api/v1/drives/test-drive").status_code == 405

