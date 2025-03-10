import time
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import BROKER_IP, PORT
from app.database import save_data

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, PORT, 60)
        self.client.loop_start()

        self.topic_callbacks = {}
        self.message_log = {}

    def on_connect(self, client, userdata, flags, rc):
        print("[DEBUG] Connected to MQTT Broker with result code:", rc)

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode()
        qos = message.qos  # Extract QoS level from message metadata
        received_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Capture ASAP
        packet_size = len(message.payload)
        print(f"[DEBUG] Received MQTT: Topic={topic}, QoS={qos}, PacketSize={packet_size} bytes, Payload={payload}")

        if qos == 1:
            if topic not in self.message_log:
                self.message_log[topic] = set()
            if payload in self.message_log[topic]:
                print(f"[DEBUG] DUPLICATE MESSAGE DETECTED for QoS 1: {payload}")
            else:
                self.message_log[topic].add(payload)

        try:
            # Save data to the database, ensuring all required fields are passed
            save_data(topic, payload, qos, received_timestamp, packet_size)
        except TypeError as e:
            print(f"[ERROR] Failed to save data: {e}")

        # Call topic-specific callbacks if registered
        if topic in self.topic_callbacks:
            for callback in self.topic_callbacks[topic]:
                callback(payload, topic)

        # Handle wildcard (#) topic callbacks
        if "#" in self.topic_callbacks:
            for callback in self.topic_callbacks["#"]:
                callback(payload, topic)


    def subscribe(self, topic, callback, qos=0):
        if topic not in self.topic_callbacks:
            self.topic_callbacks[topic] = []
            self.client.subscribe(topic, qos)
        self.topic_callbacks[topic].append(callback)

    def publish(self, topic, message, qos=0):
        """Publish a message and track its send time."""
        self.message_log[topic] = time.time()
        self.client.publish(topic, message, qos=qos)

mqtt_client = MQTTClient()
