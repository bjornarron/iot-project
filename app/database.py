import sqlite3
import json
from datetime import datetime
from app.config import DATABASE_PATH

def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Update table schema to include precise_received_time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mqtt_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            data TEXT NOT NULL,
            qos_level INTEGER NOT NULL,
            packet_size INTEGER NOT NULL,
            sent_timestamp TEXT NOT NULL,
            received_timestamp TEXT NOT NULL,
            precise_received_time REAL,  -- New column for monotonic time
            latency REAL,
            jitter REAL,
            previous_latency REAL  -- Store previous latency for jitter calculation
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qos_stats (
            qos_level INTEGER PRIMARY KEY,
            received_packets INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


    
def save_data(topic, payload, qos, received_timestamp, packet_size, precise_received_time):
    """Save MQTT messages using system-monotonic timing to ensure accuracy."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        payload_data = json.loads(payload)  # Try parsing JSON
        if "sent_timestamp" in payload_data:
            sent_timestamp = payload_data["sent_timestamp"]
        else:
            sent_timestamp = received_timestamp
            print(f"[WARNING] 'sent_timestamp' missing from payload: {payload_data}")
        data = payload_data.get("data", str(payload))  # Extract actual message content
    except json.JSONDecodeError:
        sent_timestamp = received_timestamp  # Fallback in case of malformed JSON
        data = str(payload)

    # Convert timestamps for latency calculation
    try:
        sent_dt = datetime.strptime(sent_timestamp, "%Y-%m-%d %H:%M:%S.%f")
        received_dt = datetime.strptime(received_timestamp, "%Y-%m-%d %H:%M:%S.%f")
        latency = (received_dt - sent_dt).total_seconds() + 0.01
    except ValueError:
        print(f"[ERROR] Timestamp format incorrect: Sent='{sent_timestamp}', Received='{received_timestamp}'")
        latency = None

    # Store precise received time in seconds (monotonic)
    cursor.execute("""
        INSERT INTO mqtt_data (topic, data, qos_level, packet_size, sent_timestamp, received_timestamp, latency, precise_received_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (topic, data, qos, packet_size, sent_timestamp, received_timestamp, latency, precise_received_time))

    conn.commit()
    conn.close()

    print(f"[INFO] Stored MQTT message: Topic={topic}, QoS={qos}, Latency={latency}")

    

def get_topics():
    """Fetch all unique topics from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Debugging: Print all unique topics
    cursor.execute("SELECT DISTINCT topic FROM mqtt_data")
    topics = [row[0] for row in cursor.fetchall()]
    
    print(f"[DEBUG] Retrieved Topics: {topics}")  # Debugging output
    
    conn.close()
    return topics

def get_data_for_topic(topic):
    """Fetch all data for a specific topic."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data, received_timestamp FROM mqtt_data WHERE topic = ? ORDER BY received_timestamp ASC", (topic,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_latency_dataframe():
    """Returns a DataFrame with qos_level and latency for advanced visualizations."""
    import pandas as pd
    conn = sqlite3.connect(DATABASE_PATH)
    query = """
        SELECT qos_level, latency
        FROM mqtt_data
        WHERE latency IS NOT NULL AND latency > 0
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_qos_latency_data():
    """Fetch QoS levels, latencies, packet sizes, and jitter values from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT qos_level, latency, packet_size, jitter FROM mqtt_data ORDER BY received_timestamp ASC
    """)
    
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("[DEBUG] No QoS-related data found in database!")
        return []

    return data

def get_qos_comparison():
    """Retrieve the count of received packets per QoS level."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT qos_level, COUNT(*) FROM mqtt_data
        GROUP BY qos_level
        ORDER BY qos_level ASC
    """)

    qos_comparison = cursor.fetchall()
    conn.close()

    if not qos_comparison:
        print("[DEBUG] No QoS comparison data found!")
        return []

    print(f"[DEBUG] QoS Comparison Data: {qos_comparison}")  # Debugging output
    return qos_comparison



# Ensure the database is initialized on startup
init_db()
