from __future__ import annotations

import json
import time

import paho.mqtt.client as mqtt

from config import BROKER, PORT, SENSOR_TOPIC


class SensorController:
    def __init__(self) -> None:
        self.sensor_key = "soil_moisture"
        self.topic_sub = SENSOR_TOPIC.replace("{plant_id}", "+")
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        _ = (client, userdata)
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            return

        if self.sensor_key not in payload:
            return

        print(
            "[controller_moisture]",
            payload.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
            payload.get("plant_id", "unknown"),
            f"soil_moisture={payload[self.sensor_key]}%",
        )

    def run(self) -> None:
        self.client.connect(BROKER, PORT)
        self.client.subscribe(self.topic_sub)
        print(f"[controller_moisture] listening: {self.topic_sub}")
        self.client.loop_forever()


def main() -> int:
    controller = SensorController()
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\n[controller_moisture] stopped")
        controller.client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
