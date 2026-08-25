from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

TelemetryField = Literal[
    "speed_rpm", "frequency_hz", "current_a", "dc_bus_voltage_v", "status_word", "fault_code"
]


class NodeMapping(BaseModel):
    node_id: str
    field: TelemetryField
    scale: float = 1.0
    offset: float = 0.0


class DriveConfig(BaseModel):
    id: str
    model: Literal["SK500P", "SK550P", "SK200E"]
    nodes: list[NodeMapping]

    @model_validator(mode="after")
    def unique_fields(self) -> DriveConfig:
        fields = [node.field for node in self.nodes]
        if len(fields) != len(set(fields)):
            raise ValueError(f"drive {self.id!r} maps a telemetry field more than once")
        return self


class OpcUaConfig(BaseModel):
    endpoint: str
    username: str | None = None
    password_env: str | None = None
    security_string: str | None = None
    timeout_seconds: float = Field(default=5.0, gt=0, le=30)

    @model_validator(mode="after")
    def endpoint_is_tcp(self) -> OpcUaConfig:
        if not self.endpoint.startswith("opc.tcp://"):
            raise ValueError("OPC UA endpoint must start with opc.tcp://")
        return self


class SimulatorConfig(BaseModel):
    seed: int = 1


class AppConfig(BaseModel):
    provider: Literal["simulator", "opcua"] = "simulator"
    poll_interval_seconds: float = Field(default=1.0, ge=0.2, le=60)
    stale_after_seconds: float = Field(default=5.0, ge=1, le=3600)
    opcua: OpcUaConfig | None = None
    simulator: SimulatorConfig = Field(default_factory=SimulatorConfig)
    drives: list[DriveConfig]

    @model_validator(mode="after")
    def required_provider_config(self) -> AppConfig:
        if self.provider == "opcua" and self.opcua is None:
            raise ValueError("opcua configuration is required for the opcua provider")
        ids = [drive.id for drive in self.drives]
        if len(ids) != len(set(ids)):
            raise ValueError("drive ids must be unique")
        return self


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    return AppConfig.model_validate(raw)
