import json
import sqlite3
import time

import paho.mqtt.client as mqtt

# MQTT settings
BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor"
COMMAND_TOPIC = f"smartplant/{PLANT_ID}/command"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status"

# Watering logic settings
MOISTURE_THRESHOLD = 35.0
STOP_LEVEL = 40.0  # threshold + small buffer
COOLDOWN_SECONDS = 20

DB_PATH = "plant_monitoring.db"

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)

is_watering = False
last_command_time = 0.0


def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plant_id TEXT,
            soil_moisture REAL,
            temperature REAL,
            humidity REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            details TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def log_activity(event_type, details):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO activity_log (timestamp, event_type, details) VALUES (?, ?, ?)",
        (time.strftime("%Y-%m-%d %H:%M:%S"), event_type, details),
    )
    connection.commit()
    connection.close()


def save_sensor_data(data):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO sensor_data (timestamp, plant_id, soil_moisture, temperature, humidity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.get("timestamp"),
            data.get("plant_id"),
            data.get("soil_moisture"),
            data.get("temperature"),
            data.get("humidity"),
        ),
    )
    connection.commit()
    connection.close()


def send_command(action, reason):
    global is_watering, last_command_time

    payload = {
        "plant_id": PLANT_ID,
        "action": action,
        "reason": reason,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    client.publish(COMMAND_TOPIC, json.dumps(payload))
    log_activity("command_sent", json.dumps(payload))
    last_command_time = time.time()

    if action == "WATER_ON":
        is_watering = True
    elif action == "WATER_OFF":
        is_watering = False

    print(f"[controller] Command sent: {action} ({reason})")


def handle_sensor_message(data):
    global is_watering

    save_sensor_data(data)

    moisture = float(data.get("soil_moisture", 0))
    print(
        "[controller] Received:",
        f"moisture={moisture},",
        f"temp={data.get('temperature')},",
        f"humidity={data.get('humidity')}",
    )

    now = time.time()

    if (
        moisture < MOISTURE_THRESHOLD
        and not is_watering
        and (now - last_command_time) >= COOLDOWN_SECONDS
    ):
        send_command("WATER_ON", "Soil moisture below threshold")

    elif moisture >= STOP_LEVEL and is_watering:
        send_command("WATER_OFF", "Soil moisture reached stop level")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print("[controller] Invalid JSON payload")
        return

    if msg.topic == SENSOR_TOPIC:
        handle_sensor_message(payload)
    elif msg.topic == STATUS_TOPIC:
        print(f"[controller] Status update: {payload}")
        log_activity("status_received", json.dumps(payload))


init_db()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(SENSOR_TOPIC)
client.subscribe(STATUS_TOPIC)

print("[controller] Connected")
print(f"[controller] Listening on: {SENSOR_TOPIC}")
print(f"[controller] Listening on: {STATUS_TOPIC}")
print(f"[controller] Sending commands to: {COMMAND_TOPIC}")

log_activity("controller_started", "Controller started and subscribed")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[controller] Stopped")
finally:
    log_activity("controller_stopped", "Controller stopped")
    client.disconnect()
