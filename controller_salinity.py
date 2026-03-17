import json
import sqlite3
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor/salinity"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status/salinity"
ALERT_TOPIC = f"smartplant/{PLANT_ID}/alert/salinity"

DB_PATH = "plant_monitoring.db"

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS salinity_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plant_id TEXT,
            value REAL,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS salinity_log (
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
        INSERT INTO salinity_log (timestamp, event_type, details)
        VALUES (?, ?, ?)
    """, (time.strftime("%Y-%m-%d %H:%M:%S"), event_type, details))
    conn.commit()
    conn.close()


def classify_salinity(value):
    if value < 0.8:
        return "LOW"
    elif value > 2.5:
        return "HIGH"
    return "NORMAL"


def save_data(data, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO salinity_data (timestamp, plant_id, value, status)
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
        "sensor": "salinity",
        "value": value,
        "status": status,
        "message": "Salinity out of normal range",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(ALERT_TOPIC, json.dumps(payload), qos=1)
    log_event("alert_sent", json.dumps(payload))


def handle_sensor_message(data):
    value = float(data.get("value", 0))
    status = classify_salinity(value)

    save_data(data, status)

    print("Received salinity =", value, f"({status})")

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
        print("salinity controller connection failed:", e)
        return

    print("Salinity Controller connected")
    print("Listening to:", SENSOR_TOPIC)

    log_event("controller_started", "salinity controller started")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Salinity Controller stopped")
    finally:
        try:
            log_event("controller_stopped", "salinity controller stopped")
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()