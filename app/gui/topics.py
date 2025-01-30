import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.mqtt_client import mqtt_client
from app.database import get_topics, get_data_for_topic

class TopicsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Discovered Topics", font=("Arial", 16)).pack(pady=10)

        # Treeview for Topics
        self.topic_listbox = ttk.Treeview(self, columns=("Topics"), show="tree")
        self.topic_listbox.pack(pady=10, fill="both", expand=True)

        # Button to View Topic Data
        self.view_button = ttk.Button(self, text="View Topic Data", bootstyle="primary", command=self.view_topic)
        self.view_button.pack(pady=5)

        # Populate Treeview with topics from the database
        self.load_topics()

        # Subscribe to all topics with a wildcard
        mqtt_client.subscribe("#", self.on_new_message)

    def load_topics(self):
        """Load topics from the database into the Treeview."""
        topics = get_topics()
        for topic in topics:
            self.topic_listbox.insert("", "end", text=topic)

    def on_new_message(self, payload, topic):
        """Callback for MQTT messages."""
        if not self.topic_exists_in_treeview(topic):
            self.controller.after(0, lambda: self.topic_listbox.insert("", "end", text=topic))

    def topic_exists_in_treeview(self, topic):
        """Check if a topic already exists in the Treeview."""
        for child in self.topic_listbox.get_children():
            if self.topic_listbox.item(child)["text"] == topic:
                return True
        return False

    def view_topic(self):
        """Open the selected topic's page."""
        selected_item = self.topic_listbox.selection()
        if selected_item:
            selected_topic = self.topic_listbox.item(selected_item)["text"]
            self.controller.show_frame("TopicDataPage", topic=selected_topic)
