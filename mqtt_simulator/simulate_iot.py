import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# MQTT broker details
MQTT_BROKER = "mqtt"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_traffic/intersection_data"


TRAFFIC_LIGHTS = [
    {'tl_id': 1, 'intersection_name': 'Apple St & Blueberry St'},
    {'tl_id': 2, 'intersection_name': 'Apple St & Potato St'},
    {'tl_id': 3, 'intersection_name': 'Apple St & Cherry St'},
    {'tl_id': 4, 'intersection_name': 'Apple St & Strawberry St'},
    {'tl_id': 5, 'intersection_name': 'Apple St & Lemon St'},
    {'tl_id': 6, 'intersection_name': 'Pineapple St & Cherry St'},
    {'tl_id': 7, 'intersection_name': 'Pineapple St & Strawberry St'},
    {'tl_id': 8, 'intersection_name': 'Pineapple St & Lemon St'},
    {'tl_id': 9, 'intersection_name': 'Pear St & Potato St'},
    {'tl_id': 10, 'intersection_name': 'Pear St & Cherry St'},
    {'tl_id': 11, 'intersection_name': 'Pear St & Strawberry St'}
]


POSSIBLE_STATUSES = ["red", "yellow", "green"]


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback function for when the client connects to the MQTT broker."""
    if rc == 0:
        print(f"[{datetime.now()}] [MQTT] Connected to broker with result code {rc}")
    else:
        print(f"[{datetime.now()}] [MQTT] Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    """Callback function for when the client disconnects from the MQTT broker."""
    print(f"[{datetime.now()}] [MQTT] Disconnected with result code {rc}")

def on_publish(client, userdata, mid, properties=None, reason_code=None):
    """Callback function for when a message is published."""
    pass

def get_random_traffic_status():
    """Returns a random status from the possible statuses."""
    return random.choice(POSSIBLE_STATUSES)

def publish_data():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Could not connect to MQTT broker: {e}")
        return

    client.loop_start()

    print(f"[{datetime.now()}] [SIMULATOR] Starting data publishing to topic: {MQTT_TOPIC}")

    try:
        while True:
            for tl_info in TRAFFIC_LIGHTS:
                tl_id = tl_info['tl_id']
                intersection_name = tl_info['intersection_name']
                
                status = get_random_traffic_status()

                payload = {
                    "tl_name": str(tl_id),
                    "timestamp": datetime.now().isoformat(),
                    "status": status
                }

                client.publish(MQTT_TOPIC, json.dumps(payload))
                print(f"[{datetime.now()}] [SIMULATOR] Published for TL ID {tl_id} ({intersection_name}): {payload}")
            
            time.sleep(10) # Publish all lights' statuses every 10 seconds

    except KeyboardInterrupt:
        print(f"[{datetime.now()}] [SIMULATOR] Exiting due to KeyboardInterrupt.")
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] An unexpected error occurred: {e}")
    finally:
        print(f"[{datetime.now()}] [SIMULATOR] Stopping MQTT loop and disconnecting.")
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    print("=== [BOOT] mqtt_simulator.py started ===")
    time.sleep(5) # Give MQTT broker time to start
    publish_data()

