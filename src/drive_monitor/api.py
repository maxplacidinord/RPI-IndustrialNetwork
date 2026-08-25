from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from drive_monitor.config import AppConfig
from drive_monitor.models import DriveTelemetry, MonitorSnapshot
from drive_monitor.providers.opcua import OpcUaProvider
from drive_monitor.providers.simulator import SimulatorProvider
from drive_monitor.service import MonitorService


def create_app(config: AppConfig) -> FastAPI:
    provider = SimulatorProvider(config) if config.provider == "simulator" else OpcUaProvider(config)
    service = MonitorService(config, provider)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await service.start()
        try:
            yield
        finally:
            await service.stop()

    app = FastAPI(
        title="NORD Drive Monitor",
        version="0.1.0",
        description="Read-only telemetry from NORD drives through a Siemens PLC.",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ready" if service.ready else "starting"}

    @app.get("/api/v1/drives", response_model=MonitorSnapshot)
    async def drives() -> MonitorSnapshot:
        return service.snapshot()

    @app.get("/api/v1/drives/{drive_id}", response_model=DriveTelemetry)
    async def drive(drive_id: str) -> DriveTelemetry:
        for item in service.snapshot().drives:
            if item.drive_id == drive_id:
                return item
        raise HTTPException(status_code=404, detail="drive not found")

    return app

