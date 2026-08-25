from __future__ import annotations


# NORD status word bits follow the PROFIdrive-style state word documented in the
# NORD bus manuals. Labels are deliberately descriptive rather than control commands.
STATUS_BITS: dict[int, str] = {
    0: "ready_to_switch_on",
    1: "ready_for_operation",
    2: "operation_enabled",
    3: "fault",
    4: "voltage_enabled",
    5: "quick_stop_inactive",
    6: "switch_on_inhibited",
    7: "warning",
    9: "remote_control_active",
    10: "setpoint_reached",
    11: "speed_limit_reached",
}


def decode_status_word(value: int | None) -> list[str]:
    if value is None:
        return []
    return [label for bit, label in STATUS_BITS.items() if value & (1 << bit)]


def signed_word(value: int) -> int:
    """Interpret an OPC/PLC unsigned word as signed 16-bit process data."""
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def scaled(value: int | float | None, factor: float = 1.0, offset: float = 0.0) -> float | None:
    return None if value is None else float(value) * factor + offset

