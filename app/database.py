import sqlite3
from datetime import datetime

DB_FILE = "mqtt_data.db"

def init_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mqtt_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_data(topic, data):
    """Save a new topic and its data to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO mqtt_data (topic, data, timestamp) VALUES (?, ?, ?)", (topic, data, timestamp))
    conn.commit()
    conn.close()

def get_topics():
    """Fetch all unique topics from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT topic FROM mqtt_data")
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics

def get_data_for_topic(topic):
    """Fetch all data for a specific topic."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT data, timestamp FROM mqtt_data WHERE topic = ? ORDER BY timestamp ASC", (topic,))
    data = cursor.fetchall()
    conn.close()
    return data

# Initialize the database when the script is run
init_db()
