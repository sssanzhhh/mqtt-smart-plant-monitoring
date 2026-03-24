# TLS defaults and MQTT client setup live here so every process uses the same
# certificate configuration.
from __future__ import annotations

import ssl
import sys
from pathlib import Path

try:
    import certifi
except ImportError:
    certifi = None

# ─────────────────────────────────────────────
#  Plant Monitoring – Central Configuration
#  All constants and plant profiles live here.
#  No other file should hardcode these values.
# ─────────────────────────────────────────────

BROKER = "broker.hivemq.com"
PORT   = 8883

TLS_CA_CERT     = None
TLS_CLIENT_CERT = None
TLS_CLIENT_KEY  = None

SENSOR_TOPIC  = "smartplant/{plant_id}/sensor"
COMMAND_TOPIC = "smartplant/{plant_id}/command"
STATUS_TOPIC  = "smartplant/{plant_id}/status"
ALERT_TOPIC   = "smartplant/{plant_id}/alerts"

DB_PATH = "plant_monitoring.db"

COOLDOWN_SECONDS = 20
PUBLISH_INTERVAL_SECONDS = 3

PLANT_PROFILES = {
    "ficus": {
        "display_name": "Ficus",
        "moisture_min":      40.0,
        "moisture_stop":     60.0,
        "moisture_warning":  30.0,
        "moisture_critical": 20.0,
        "nitrogen":    (150, 300),
        "phosphorus":  (50,  150),
        "potassium":   (100, 250),
        "soil_ph":  (5.5, 7.0),
        "salinity": (0.0, 1.5),
        "root_temperature": (18.0, 28.0),
    },
    "cactus": {
        "display_name": "Cactus",
        "moisture_min":      15.0,
        "moisture_stop":     25.0,
        "moisture_warning":  10.0,
        "moisture_critical":  5.0,
        "nitrogen":   (50,  150),
        "phosphorus": (20,   80),
        "potassium":  (50,  150),
        "soil_ph":  (6.0, 7.5),
        "salinity": (0.0, 2.5),
        "root_temperature": (15.0, 35.0),
    },
}

def build_plant_id(plant_type: str) -> str:
    return f"plant-{plant_type}-001"

DEFAULT_PLANT = "ficus"


def configure_mqtt_client_tls(client) -> None:
    tls_kwargs = {"tls_version": ssl.PROTOCOL_TLS_CLIENT}
    ca_source = "system defaults"

    if TLS_CA_CERT:
        tls_kwargs["ca_certs"] = TLS_CA_CERT
        ca_source = TLS_CA_CERT
    elif certifi is not None:
        tls_kwargs["ca_certs"] = certifi.where()
        ca_source = "certifi"

    if TLS_CLIENT_CERT:
        tls_kwargs["certfile"] = TLS_CLIENT_CERT
    if TLS_CLIENT_KEY:
        tls_kwargs["keyfile"] = TLS_CLIENT_KEY

    client.tls_set(**tls_kwargs)
    client.tls_insecure_set(False)
    process_name = Path(sys.argv[0]).name or "process"
    print(f"[{process_name}] TLS enabled, certificate verification enforced, CA source: {ca_source}")
