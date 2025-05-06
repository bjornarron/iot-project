import time
from datetime import datetime
import paho.mqtt.client as mqtt
import ssl
from app.config import BROKER_IP, PORT
from app.database import save_data
from app.config import MQTT_USERNAME, MQTT_PASSWORD

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        #self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        #self.client.tls_insecure_set(True)        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, PORT, 60)
        self.client.loop_start()

        self.topic_callbacks = {}
        self.message_log = {}
        self.current_qos = 0  # Track current QoS for `#` wildcard subscription

    def on_connect(self, client, userdata, flags, rc):
        print("[DEBUG] Connected to MQTT Broker with result code:", rc)

    def on_message(self, client, userdata, message):
        """Process MQTT messages and track timestamps more accurately."""
        topic = message.topic
        payload = message.payload.decode()
        qos = message.qos
        packet_size = len(message.payload)

        # Use time.monotonic() to track precise message arrival time
        received_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        precise_received_time = time.monotonic()

        print(f"[DEBUG] Received MQTT: Topic={topic}, QoS={qos}, PacketSize={packet_size} bytes, Payload={payload}")
        print(f"[DEBUG] Local system time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        try:
            save_data(topic, payload, qos, received_timestamp, packet_size, precise_received_time)
        except TypeError as e:
            print(f"[ERROR] Failed to save data: {e}")

        print(f"[INFO] Message successfully processed for {topic} at QoS {qos}")


    def subscribe(self, topic, callback, qos=0):
        """Ensure proper resubscription to all topics when changing QoS."""
        if topic == "#" and qos != self.current_qos:
            print(f"[INFO] Changing QoS for `#`: Unsubscribing and resubscribing with QoS {qos}")
            
            # First, check if the client is already subscribed before unsubscribing
            self.client.unsubscribe("#")
            
            # Allow some time for the broker to process the unsubscription
            time.sleep(1)

            # Resubscribe with the new QoS level
            self.client.subscribe("#", qos)
            self.current_qos = qos  # Track the current QoS level
            print(f"[INFO] Successfully resubscribed to `#` with QoS {qos}")

        # Ensure the callback is registered
        if topic not in self.topic_callbacks:
            self.topic_callbacks[topic] = []
        self.topic_callbacks[topic].append(callback)

        print(f"[DEBUG] Subscription active for {topic} at QoS {qos}")

    def publish(self, topic, message, qos=0):
        """Publish a message and track its send time."""
        self.message_log[topic] = time.time()
        self.client.publish(topic, message, qos=qos)

mqtt_client = MQTTClient()
