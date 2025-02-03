import os

# MQTT Configuration
BROKER_IP = "172.20.10.11"  # Change this to your actual broker IP
PORT = 1883

# Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Ensure the database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATABASE_DIR, "data.db")