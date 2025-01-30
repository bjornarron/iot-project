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

        # Track topic-specific callbacks
        self.topic_callbacks = {}

    def on_connect(self, client, userdata, flags, rc):
        print("[DEBUG] Connected to MQTT Broker with result code:", rc)

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode()

        print(f"[DEBUG] Message received: Topic={topic}, Payload={payload}")

        # Save data to the database
        save_data(topic, payload)

        # Route messages to appropriate callbacks
        if topic in self.topic_callbacks:
            for callback in self.topic_callbacks[topic]:
                callback(payload, topic)

        # If subscribed to wildcard (#), call all wildcard callbacks
        if "#" in self.topic_callbacks:
            for callback in self.topic_callbacks["#"]:
                callback(payload, topic)

    def subscribe(self, topic, callback):
        """Subscribe to a topic and store its callback."""
        if topic not in self.topic_callbacks:
            print(f"[DEBUG] Subscribing to topic: {topic}")
            self.topic_callbacks[topic] = []
            self.client.subscribe(topic)
        self.topic_callbacks[topic].append(callback)

    def publish(self, topic, message):
        """Publish a message to a topic."""
        print(f"[DEBUG] Publishing message: Topic={topic}, Payload={message}")
        self.client.publish(topic, message)

mqtt_client = MQTTClient()
