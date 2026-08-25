from __future__ import annotations

import os
from datetime import UTC, datetime

from asyncua import Client

from drive_monitor.config import AppConfig, DriveConfig
from drive_monitor.decode import decode_status_word, scaled
from drive_monitor.models import DriveTelemetry, Quality


class OpcUaProvider:
    """Read configured PLC nodes. This class contains no OPC UA write operation."""

    def __init__(self, config: AppConfig) -> None:
        assert config.opcua is not None
        self._settings = config.opcua
        self._drives = config.drives
        self._client = Client(self._settings.endpoint, timeout=self._settings.timeout_seconds)

    async def connect(self) -> None:
        if self._settings.username:
            self._client.set_user(self._settings.username)
        if self._settings.password_env:
            password = os.environ.get(self._settings.password_env)
            if password is None:
                raise RuntimeError(
                    f"required password environment variable {self._settings.password_env!r} is unset"
                )
            self._client.set_password(password)
        if self._settings.security_string:
            await self._client.set_security_string(self._settings.security_string)
        await self._client.connect()

    async def close(self) -> None:
        await self._client.disconnect()

    async def read_all(self) -> list[DriveTelemetry]:
        return [await self._read_drive(drive) for drive in self._drives]

    async def _read_drive(self, drive: DriveConfig) -> DriveTelemetry:
        telemetry = DriveTelemetry(drive_id=drive.id, model=drive.model)
        try:
            # One Read service call minimizes PLC communication load. AttributeId.Value is read-only.
            nodes = [self._client.get_node(item.node_id) for item in drive.nodes]
            results = await self._client.read_attributes(nodes)
            for mapping, result in zip(drive.nodes, results, strict=True):
                if result.StatusCode.is_bad():
                    raise RuntimeError(f"{mapping.node_id}: {result.StatusCode.name}")
                value = result.Value.Value if result.Value else None
                converted = scaled(value, mapping.scale, mapping.offset)
                if mapping.field in {"status_word", "fault_code"}:
                    converted = None if converted is None else int(converted)
                setattr(telemetry, mapping.field, converted)
            telemetry.status_flags = decode_status_word(telemetry.status_word)
            telemetry.fault_text = "No fault" if telemetry.fault_code == 0 else None
            telemetry.observed_at = datetime.now(UTC)
            return telemetry
        except Exception as exc:
            telemetry.quality = Quality.BAD
            telemetry.error = f"read failed: {exc}"
            return telemetry
