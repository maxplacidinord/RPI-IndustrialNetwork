from __future__ import annotations

import math
import random
import time

from drive_monitor.config import AppConfig
from drive_monitor.decode import decode_status_word
from drive_monitor.models import DriveTelemetry


class SimulatorProvider:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._random = random.Random(config.simulator.seed)
        self._started = time.monotonic()

    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def read_all(self) -> list[DriveTelemetry]:
        elapsed = time.monotonic() - self._started
        result = []
        for index, drive in enumerate(self._config.drives):
            speed = 1400 + 100 * math.sin(elapsed / 8 + index)
            speed += self._random.uniform(-2, 2)
            status = 0b0000011000110111
            result.append(
                DriveTelemetry(
                    drive_id=drive.id,
                    model=drive.model,
                    speed_rpm=round(speed, 1),
                    frequency_hz=round(speed / 30, 2),
                    current_a=round(2.5 + index * 0.4, 2),
                    dc_bus_voltage_v=565.0,
                    status_word=status,
                    status_flags=decode_status_word(status),
                    fault_code=0,
                    fault_text="No fault",
                )
            )
        return result
