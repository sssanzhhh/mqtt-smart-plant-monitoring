from __future__ import annotations

import json
import ssl
import time

import paho.mqtt.client as mqtt

from config import (
    BROKER, PORT, SENSOR_TOPIC, COMMAND_TOPIC, ALERT_TOPIC, PLANT_PROFILES, COOLDOWN_SECONDS,
)


class SensorController:
    def __init__(self) -> None:
        self.sensor_key = "soil_moisture"
        self.topic_sub = SENSOR_TOPIC.replace("{plant_id}", "+")
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.tls_insecure_set(False)
        self.client.on_message = self.on_message

        self.is_watering: dict[str, bool] = {}
        self.last_cmd_time: dict[str, float] = {}
        self.active_alerts: dict[str, str] = {}

    def _publish_alert(self, plant_id: str, plant_type: str, severity: str, value: float, message: str) -> None:
        if self.active_alerts.get(plant_id) == severity:
            return
        self.active_alerts[plant_id] = severity
        topic = ALERT_TOPIC.format(plant_id=plant_id)
        payload = {
            "plant_id": plant_id,
            "plant_type": plant_type,
            "alert_type": "LOW_MOISTURE",
            "severity": severity,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.client.publish(topic, json.dumps(payload))
        print(f"[controller_moisture] ALERT [{severity}] moisture={value}%")

    def _clear_alert(self, plant_id: str) -> None:
        self.active_alerts.pop(plant_id, None)

    def _send_command(self, plant_id: str, action: str, reason: str) -> None:
        topic = COMMAND_TOPIC.format(plant_id=plant_id)
        payload = {
            "plant_id": plant_id,
            "action": action,
            "reason": reason,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.client.publish(topic, json.dumps(payload))
        self.last_cmd_time[plant_id] = time.time()
        self.is_watering[plant_id] = action == "WATER_ON"
        print(f"[controller_moisture] command={action} plant={plant_id} reason={reason}")

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        _ = (client, userdata)
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            return

        if self.sensor_key not in payload:
            return

        plant_id = payload.get("plant_id", "unknown")
        plant_type = payload.get("plant_type", "ficus")
        profile = PLANT_PROFILES.get(plant_type)
        if profile is None:
            return

        moisture = float(payload[self.sensor_key])
        watering = self.is_watering.get(plant_id, False)
        now = time.time()

        print(
            "[controller_moisture]",
            payload.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
            plant_id,
            f"soil_moisture={moisture}%",
            f"watering={watering}",
        )

        if moisture < profile["moisture_critical"] and not watering:
            self._publish_alert(plant_id, plant_type, "CRITICAL", moisture, f"Soil moisture critically low: {moisture}%")
        elif moisture < profile["moisture_warning"] and not watering:
            self._publish_alert(plant_id, plant_type, "WARNING", moisture, f"Soil moisture low: {moisture}%")
        else:
            self._clear_alert(plant_id)

        if (
            moisture < profile["moisture_min"]
            and not watering
            and (now - self.last_cmd_time.get(plant_id, 0)) >= COOLDOWN_SECONDS
        ):
            self._send_command(plant_id, "WATER_ON", "Soil moisture below threshold")
        elif moisture >= profile["moisture_stop"] and watering:
            self._send_command(plant_id, "WATER_OFF", "Soil moisture reached stop level")

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
