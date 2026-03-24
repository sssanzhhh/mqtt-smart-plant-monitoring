# MQTT Smart Plant Monitoring System

## Aims

This project aims to design and implement an enhanced IoT-based smart plant monitoring system that simulates real-world sensor behaviour, applies plant-specific intelligent watering logic, and provides a real-time graphical interface for environmental health assessment.

---

## Objectives

- Extend the existing MQTT publish/subscribe architecture to support advanced soil parameters (NPK, pH, salinity, root temperature).
- Implement multi-plant support with configurable, species-specific threshold profiles.
- Develop a severity-based alerting system (INFO / WARNING / CRITICAL) published over dedicated MQTT topics.
- Persist all sensor readings and system events in a structured SQLite database, including severity metadata.
- Deliver a real-time Pygame dashboard that visually reflects plant health and watering status.

---

## Research Questions

- How can a lightweight MQTT architecture be extended to support heterogeneous IoT sensor data without redesigning the core system?
- To what extent can species-specific threshold profiles improve watering accuracy compared to a universal threshold?
- How effectively can a local simulation reproduce biologically realistic sensor behaviour?

---

## Methodology

The system follows an incremental extension methodology. The original two-component architecture (Publisher + Controller) was retained and extended rather than replaced.

A centralised configuration file (`config.py`) defines plant profiles and MQTT constants. Sensor simulation includes realistic drift behaviours. Controllers evaluate plant-specific thresholds and publish alerts. The dashboard passively subscribes to MQTT topics.

---

## 🔐 Security Enhancement (TLS Encryption)

TLS encryption has been integrated into MQTT communication to ensure secure data transmission.

### Key Changes

- Port changed: **1883 → 8883**
- TLS v1.2+ enforced
- CA certificate validation enabled

### Implementation Example

```python
client.tls_set(
    ca_certs="ca.crt",
    certfile=None,
    keyfile=None,
)
client.tls_insecure_set(False)

client.connect(broker, 8883)
```

### Design Principle

TLS was added **without changing system architecture**, preserving:

- OOP structure  
- publish/subscribe logic  
- controller processing  
- database pipeline  

---

## System Architecture

```
Publisher_*  ──┐
               ├──► MQTT Broker (HiveMQ, TLS 8883) ──► Controller_* ──► SQLite DB
Publisher_*  ──┘              │
                             └──────────────────────► Dashboard (Pygame)
```

---

## Components

- **publisher_*.py** — Simulated IoT sensors generating plant data and publishing via MQTT.
- **controller_*.py** — Processes sensor data, applies thresholds, triggers watering and alerts.
- **dashboard.py** — Real-time Pygame interface displaying plant health.
- **config.py** — Central configuration (MQTT + plant profiles).
- **inspect_db.py** — CLI tool for database inspection.
- **main.py** — Runs the full system.

---

## Multi-Plant Logic

Each plant type is defined in `config.py` via `PLANT_PROFILES`.

| Parameter        | Ficus 🌿 | Cactus 🌵 |
|------------------|----------|----------|
| Moisture start   | 40%      | 15%      |
| Moisture stop    | 60%      | 25%      |
| Nitrogen         | 150–300  | 50–150   |
| Phosphorus       | 50–150   | 20–80    |
| Potassium        | 100–250  | 50–150   |
| pH               | 5.5–7.0  | 6.0–7.5  |
| Salinity         | 0.0–1.5  | 0.0–2.5  |
| Root temp        | 18–28°C  | 15–35°C  |

---

## Alert System

Alerts are published to:

```
smartplant/{plant_id}/alerts
```

| Severity | Condition |
|----------|----------|
| INFO     | Normal range |
| WARNING  | Slight deviation |
| CRITICAL | Large deviation |

---

## Technologies Used

- Python 3.10+
- MQTT (paho-mqtt)
- SQLite
- Pygame
- JSON
- TLS (SSL)

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the System

```bash
python main.py
```

---

## Database

Tables:

- `sensor_data` — sensor readings  
- `activity_log` — alerts, commands, events  

```bash
python inspect_db.py
```

---

## About

MQTT-based Smart Plant Monitoring and Automatic Watering System using Python and SQLite.

Implements secure publish/subscribe communication via HiveMQ broker with TLS encryption.
