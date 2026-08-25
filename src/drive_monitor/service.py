from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import UTC, datetime

from drive_monitor.config import AppConfig
from drive_monitor.models import DriveTelemetry, MonitorSnapshot, Quality
from drive_monitor.providers.base import TelemetryProvider

LOGGER = logging.getLogger(__name__)


class MonitorService:
    def __init__(self, config: AppConfig, provider: TelemetryProvider) -> None:
        self._config = config
        self._provider = provider
        self._drives: list[DriveTelemetry] = []
        self._task: asyncio.Task[None] | None = None
        self._ready = asyncio.Event()

    async def start(self) -> None:
        await self._provider.connect()
        self._task = asyncio.create_task(self._poll(), name="drive-telemetry-poll")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
        await self._provider.close()

    async def _poll(self) -> None:
        while True:
            try:
                self._drives = await self._provider.read_all()
                self._ready.set()
            except Exception:
                LOGGER.exception("telemetry polling cycle failed")
            await asyncio.sleep(self._config.poll_interval_seconds)

    def snapshot(self) -> MonitorSnapshot:
        now = datetime.now(UTC)
        drives = [item.model_copy(deep=True) for item in self._drives]
        for drive in drives:
            age = (now - drive.observed_at).total_seconds()
            if drive.quality == Quality.GOOD and age > self._config.stale_after_seconds:
                drive.quality = Quality.STALE
        return MonitorSnapshot(generated_at=now, drives=drives)

    @property
    def ready(self) -> bool:
        return self._ready.is_set()
