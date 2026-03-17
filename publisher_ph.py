import json
import random
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
PLANT_ID = "plant-001"

SENSOR_TOPIC = f"smartplant/{PLANT_ID}/sensor/soil_ph"
STATUS_TOPIC = f"smartplant/{PLANT_ID}/status/soil_ph"

soil_ph = 6.4

app_version2 = mqtt.CallbackAPIVersion.VERSION2
client = mqtt.Client(callback_api_version=app_version2)


def publish_status(message: str):
    payload = {
        "plant_id": PLANT_ID,
        "sensor": "soil_ph",
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(STATUS_TOPIC, json.dumps(payload), qos=1)


def main():
    global soil_ph

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as e:
        print("soil_ph publisher connection failed:", e)
        return

    print("Soil pH Publisher connected")
    print("Publishing to:", SENSOR_TOPIC)

    publish_status("soil_ph publisher started")

    try:
        while True:
            soil_ph += random.uniform(-0.08, 0.08)
            soil_ph = max(4.5, min(8.5, soil_ph))

            reading = {
                "plant_id": PLANT_ID,
                "sensor": "soil_ph",
                "value": round(soil_ph, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            client.publish(SENSOR_TOPIC, json.dumps(reading), qos=1)
            print("Sent soil_ph =", reading["value"])

            time.sleep(5)

    except KeyboardInterrupt:
        print("Soil pH Publisher stopped")
    finally:
        try:
            publish_status("soil_ph publisher stopped")
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()