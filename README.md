# Raspberry Pi NORD Drive Monitor

A read-only telemetry gateway for NORD SK 500P, SK 550P and SK 200E drives controlled by a
Siemens S7-1200. The Pi reads drive values exported by the PLC's OPC UA server and serves them
as JSON. It has no drive-control endpoint and its OPC UA provider implements reads only.

This is an educational lab tool, not a safety or control system. Keep the PLC and drives behind
an industrial firewall, use a mirror/TAP or a dedicated monitoring VLAN where appropriate, and
never rely on this service for protective functions.

## Why OPC UA

PROFINET IO cyclic frames belong to the PLC/controller relationship. A second controller should
not claim the drives. Reading a small, explicit OPC UA interface from the existing S7-1200 is
predictable and keeps control ownership with the PLC. S7-1200 firmware V4.4 and newer can provide
an OPC UA server; availability/licensing depends on the exact CPU and TIA Portal version.

## Quick start (simulator)

On Raspberry Pi OS Bookworm or another Python 3.11+ system:

```bash
sudo apt update
sudo apt install -y python3-venv
git clone https://github.com/maxplacidinord/RPI-IndustrialNetwork.git
cd RPI-IndustrialNetwork
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp config.example.yaml config.yaml
drive-monitor --host 0.0.0.0 --port 8080
```

Then open `http://PI_ADDRESS:8080/docs`, or request:

```bash
curl http://PI_ADDRESS:8080/api/v1/drives
```

The example configuration starts in simulator mode. The only application routes are `GET`
routes; POST, PUT, PATCH and DELETE return HTTP 405.

## Connecting the S7-1200

1. In TIA Portal, collect each drive's input/status process data into a dedicated global DB,
   for example `DriveTelemetry`. Expose only the required members: actual speed, actual
   frequency, current, DC-link voltage, status word, and current fault code.
2. Enable the CPU OPC UA server and create a server interface containing those DB members.
   Give the monitoring account read permission only. Prefer `Basic256Sha256` with signing and
   encryption, and trust the Pi client certificate on the PLC.
3. Copy `config.example.yaml` to the ignored `config.yaml`. Change `provider` to `opcua`, set the
   PLC endpoint, credentials, security material, and the exact NodeIds shown by the PLC server.
4. Verify the mapping while the drive is safely stationary, then at a known reference speed.
   NORD process values can be raw, normalized, or engineering units depending on the telegram
   and PLC program. Put conversion in each node's `scale` and `offset`; do not assume the sample
   mapping matches the machine.
5. Start at a one-second polling interval. Confirm in TIA Portal that communication load remains
   acceptable before reducing it. This project enforces a minimum interval of 200 ms.

Secrets are referenced by environment-variable name, never stored in YAML:

```yaml
provider: opcua
opcua:
  endpoint: opc.tcp://192.168.0.10:4840
  username: drive_monitor
  password_env: DRIVE_MONITOR_OPCUA_PASSWORD
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Poller readiness |
| GET | `/api/v1/drives` | Latest snapshot of all configured drives |
| GET | `/api/v1/drives/{id}` | Latest snapshot of one drive |

Quality is `good`, `bad`, or `stale`. A failed node read is returned as bad quality with an error
message instead of silently retaining an old value.

## Tests

```bash
ruff check .
pytest
```

## Deployment

The sample [systemd unit](deploy/drive-monitor.service) runs under a dedicated unprivileged user
with filesystem and kernel hardening. Install the project in `/opt/drive-monitor`, place the
configuration in `/etc/drive-monitor/config.yaml`, credentials in `/etc/drive-monitor/secrets`,
then copy and enable the unit. Restrict TCP 8080 to the lab/management subnet with the host or
network firewall.

## Documentation used

- NORD BU0620, *Industrial Ethernet bus interface for NORDAC PRO (SK 500P)*
- NORD BU0590/BU2400, *PROFINET IO bus interface* (including PZD OUT status/actual-value layout)
- NORD BU0600, *NORDAC PRO SK 500P series manual*
- NORD BU0200, *NORDAC FLEX SK 200E manual*
- Siemens, *S7-1200 Programmable Controller System Manual*, OPC UA server section

Always check the revisions matching the installed drive firmware, bus option and PLC CPU. The
repository deliberately does not hard-code a fault-code table because the meaning and source
can vary by device family/firmware; export a human-readable PLC diagnostic string if needed.
