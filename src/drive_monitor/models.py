from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Quality(StrEnum):
    GOOD = "good"
    BAD = "bad"
    STALE = "stale"


class DriveTelemetry(BaseModel):
    drive_id: str
    model: str
    speed_rpm: float | None = None
    frequency_hz: float | None = None
    current_a: float | None = None
    dc_bus_voltage_v: float | None = None
    status_word: int | None = Field(default=None, ge=0, le=65535)
    status_flags: list[str] = Field(default_factory=list)
    fault_code: int | None = None
    fault_text: str | None = None
    quality: Quality = Quality.GOOD
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error: str | None = None


class MonitorSnapshot(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    drives: list[DriveTelemetry]
