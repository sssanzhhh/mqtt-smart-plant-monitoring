import json
import random
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor/salinity"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status/salinity"

salinity = 1.4

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)


def publish_status(message: str):
    payload = {
        "plant_id": PLANT_ID,
        "sensor": "salinity",
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1)


def main():
    global salinity

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as e:
        print("salinity publisher connection failed:", e)
        return

    print("Salinity Publisher connected")
    print("Publishing to:", SENSOR_TOPIC)

    publish_status("salinity publisher started")

    try:
        while True:
            salinity += random.uniform(-0.10, 0.10)
            salinity = max(0.2, min(4.0, salinity))

            reading = {
                "plant_id": PLANT_ID,
                "sensor": "salinity",
                "value": round(salinity, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            client.publish(SENSOR_TOPIC, json.dumps(reading), qos=1)
            print("Sent salinity =", reading["value"])

            time.sleep(5)

    except KeyboardInterrupt:
        print("Salinity Publisher stopped")
    finally:
        try:
            publish_status("salinity publisher stopped")
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()