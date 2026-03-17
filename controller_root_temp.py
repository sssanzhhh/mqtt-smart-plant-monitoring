import json
import sqlite3
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor/root_temperature"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status/root_temperature"
ALERT_TOPIC = f"smartplant/{PLANT_ID}/alert/root_temperature"

DB_PATH = "plant_monitoring.db"

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS root_temperature_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plant_id TEXT,
            value REAL,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS root_temperature_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_event(event_type, details):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO root_temperature_log (timestamp, event_type, details)
        VALUES (?, ?, ?)
    """, (time.strftime("%Y-%m-%d %H:%M:%S"), event_type, details))
    conn.commit()
    conn.close()


def classify_root_temperature(value):
    if value < 18:
        return "LOW"
    elif value > 28:
        return "HIGH"
    return "NORMAL"


def save_data(data, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO root_temperature_data (timestamp, plant_id, value, status)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("timestamp"),
        data.get("plant_id"),
        data.get("value"),
        status,
    ))
    conn.commit()
    conn.close()


def publish_alert(value, status):
    payload = {
        "plant_id": PLANT_ID,
        "sensor": "root_temperature",
        "value": value,
        "status": status,
        "message": "Root-zone temperature out of normal range",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(ALERT_TOPIC, json.dumps(payload), qos=1)
    log_event("alert_sent", json.dumps(payload))


def handle_sensor_message(data):
    value = float(data.get("value", 0))
    status = classify_root_temperature(value)

    save_data(data, status)

    print("Received root_temperature =", value, f"({status})")

    if status != "NORMAL":
        publish_alert(value, status)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except Exception as e:
        print("Invalid JSON:", e)
        return

    if msg.topic == SENSOR_TOPIC:
        handle_sensor_message(payload)
    elif msg.topic == STATUS_TOPIC:
        print("Status update:", payload)
        log_event("status_received", json.dumps(payload))


def main():
    init_db()
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.subscribe(SENSOR_TOPIC, qos=1)
        client.subscribe(STATUS_TOPIC, qos=1)
    except Exception as e:
        print("root temperature controller connection failed:", e)
        return

    print("Root Temperature Controller connected")
    print("Listening to:", SENSOR_TOPIC)

    log_event("controller_started", "root_temperature controller started")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Root Temperature Controller stopped")
    finally:
        try:
            log_event("controller_stopped", "root_temperature controller stopped")
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()