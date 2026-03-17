import json
import random
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor/root_temperature"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status/root_temperature"

root_temperature = 23.0

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)


def publish_status(message: str):
    payload = {
        "plant_id": PLANT_ID,
        "sensor": "root_temperature",
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1)


def main():
    global root_temperature

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as e:
        print("root temperature publisher connection failed:", e)
        return

    print("Root Temperature Publisher connected")
    print("Publishing to:", SENSOR_TOPIC)

    publish_status("root_temperature publisher started")

    try:
        while True:
            root_temperature += random.uniform(-0.30, 0.30)
            root_temperature = max(10.0, min(35.0, root_temperature))

            reading = {
                "plant_id": PLANT_ID,
                "sensor": "root_temperature",
                "value": round(root_temperature, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            client.publish(SENSOR_TOPIC, json.dumps(reading), qos=1)
            print("Sent root_temperature =", reading["value"])

            time.sleep(5)

    except KeyboardInterrupt:
        print("Root Temperature Publisher stopped")
    finally:
        try:
            publish_status("root_temperature publisher stopped")
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()