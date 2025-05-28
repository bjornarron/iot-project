import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import ssl

# MQTT Broker details
BROKER = "10.245.30.78"  #broker's address
PORT = 8883  #MQTT port
QOS = 2  # QoS level
TOPIC = "/home/bedroom/temp"
CLIENT_ID = f"sensor_publisher{random.randint(0, 1000)}"
PACKET_COUNT = 100
username = "admin"
password = "admin"

#TLS configuration
tls_version = ssl.PROTOCOL_TLSv1_2

# Latency tracking
data_stats = {"latencies": [], "received": 0}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC, qos=QOS)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    recv_time = time.time()
    payload = json.loads(msg.payload.decode())
    sent_time = datetime.strptime(payload["sent_timestamp"], '%Y-%m-%d %H:%M:%S.%f').timestamp()
    latency = recv_time - sent_time
    userdata["latencies"].append(latency)
    userdata["received"] += 1

def generate_payload(packet_size):
    """Generates a JSON payload of approximately packet_size bytes"""
    base_data = {
        "sent_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "data": round(random.uniform(10.0, 25.0), 2),
        "packet_size": packet_size,
    }
    base_json = json.dumps(base_data)
    remaining_size = packet_size - len(base_json.encode("utf-8"))
    if remaining_size > 0:
        base_data["filler"] = "X" * remaining_size  # Adding filler characters
    return json.dumps(base_data)

def publish_data(client):
    for i in range(PACKET_COUNT):
        packet_size = 1
        payload = generate_payload(packet_size)
        result = client.publish(TOPIC, payload, qos=QOS)
        status = result.rc
        if status == 0:
            print(f"Sent message of size {len(payload.encode('utf-8'))} bytes to topic `{TOPIC}` with QoS {QOS}")
        else:
            print(f"Failed to send message to topic {TOPIC}")
        time.sleep(1)

def print_results():
    received = data_stats["received"]
    lost = PACKET_COUNT - received
    avg_latency = sum(data_stats["latencies"]) / received if received else float('inf')
    print(f"Sent={PACKET_COUNT}, Received={received}, Lost={lost}, Avg Latency={avg_latency:.4f}s")

if __name__ == "__main__":
    client = mqtt.Client(CLIENT_ID, userdata=data_stats)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    try:
        publish_data(client)
        time.sleep(5)  # Allow time for messages to be received
        print_results()
    finally:
        print("Disconnecting...")
        client.loop_stop()
        client.disconnect()
