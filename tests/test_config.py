import pytest
from pydantic import ValidationError

from drive_monitor.config import AppConfig


def test_opcua_provider_requires_settings() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"provider": "opcua", "drives": []})


def test_duplicate_drive_ids_are_rejected() -> None:
    drive = {"id": "same", "model": "SK500P", "nodes": []}
    with pytest.raises(ValidationError):
        AppConfig.model_validate({"provider": "simulator", "drives": [drive, drive]})


def test_non_opc_endpoint_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(
            {
                "provider": "opcua",
                "opcua": {"endpoint": "http://plc.local"},
                "drives": [],
            }
        )
