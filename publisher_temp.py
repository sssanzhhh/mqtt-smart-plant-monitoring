from __future__ import annotations

import json
import random
import sys
import time

import paho.mqtt.client as mqtt

from config import (
    BROKER, DEFAULT_PLANT, PLANT_PROFILES, PORT, PUBLISH_INTERVAL_SECONDS, SENSOR_TOPIC,
    build_plant_id, configure_mqtt_client_tls,
)


class SensorPublisher:
    def __init__(self, plant_type: str) -> None:
        plant_type = plant_type.lower()
        if plant_type not in PLANT_PROFILES:
            raise ValueError(f"Unknown plant type: {plant_type}")
        self.plant_type = plant_type
        self.plant_id = build_plant_id(plant_type)
        self.topic = SENSOR_TOPIC.format(plant_id=self.plant_id)
        self.value = random.uniform(22.0, 26.0)
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        configure_mqtt_client_tls(self.client)

    def _next_value(self) -> float:
        self.value += random.uniform(-0.25, 0.25)
        self.value = max(15.0, min(40.0, self.value))
        return round(self.value, 2)

    def publish(self) -> None:
        self.client.connect(BROKER, PORT)
        self.client.loop_start()
        print(f"[publisher_temp] topic: {self.topic}")
        try:
            while True:
                payload = {
                    "plant_id": self.plant_id,
                    "plant_type": self.plant_type,
                    "temperature": self._next_value(),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                self.client.publish(self.topic, json.dumps(payload))
                print(f"[publisher_temp] sent: {payload['temperature']}C")
                time.sleep(PUBLISH_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[publisher_temp] stopped")
        finally:
            self.client.loop_stop()
            self.client.disconnect()


def main() -> int:
    plant_type = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PLANT
    publisher = SensorPublisher(plant_type)
    publisher.publish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
