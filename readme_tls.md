# MQTT Smart Plant Monitoring System

## Aims

This project aims to design and implement an enhanced IoT-based smart plant monitoring system that simulates real-world sensor behaviour, applies plant-specific intelligent watering logic, and provides a real-time graphical interface for environmental health assessment.

---

## Objectives

1. Extend the existing MQTT publish/subscribe architecture to support advanced soil parameters (NPK, pH, salinity, root temperature).
2. Implement multi-plant support with configurable, species-specific threshold profiles.
3. Develop a severity-based alerting system (INFO / WARNING / CRITICAL) published over dedicated MQTT topics.
4. Persist all sensor readings and system events in a structured SQLite database, including severity metadata.
5. Deliver a real-time Pygame dashboard that visually reflects plant health and watering status.

---

## 🔐 Security Enhancement (TLS Encryption)

TLS encryption has been integrated into MQTT communication.

- Port changed: 1883 → 8883  
- TLS v1.2+ enforced  
- CA certificate validation enabled  

Example:

```python
client.tls_set(
    ca_certs="ca.crt",
    certfile=None,
    keyfile=None,
)
client.tls_insecure_set(False)

client.connect(broker, 8883)
```

---

## System Architecture

```
Publisher_*  ──┐
               ├──► MQTT Broker (TLS 8883) ──► Controller_* ──► SQLite DB
Publisher_*  ──┘              │
                             └──────────────► Dashboard
```

---

## Technologies

- Python
- MQTT (paho-mqtt)
- SQLite
- Pygame
- TLS (SSL)

---

## Run

```bash
python main.py
```
