from __future__ import annotations

from typing import Protocol

from drive_monitor.models import DriveTelemetry


class TelemetryProvider(Protocol):
    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def read_all(self) -> list[DriveTelemetry]: ...
