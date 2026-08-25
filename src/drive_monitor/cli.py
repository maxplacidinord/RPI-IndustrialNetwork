from __future__ import annotations

import argparse
import logging
import os

import uvicorn

from drive_monitor.api import create_app
from drive_monitor.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only NORD drive telemetry gateway")
    parser.add_argument("--config", default=os.environ.get("DRIVE_MONITOR_CONFIG", "config.yaml"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    uvicorn.run(create_app(load_config(args.config)), host=args.host, port=args.port)


if __name__ == "__main__":
    main()

