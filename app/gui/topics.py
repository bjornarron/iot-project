import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.mqtt_client import mqtt_client
from app.database import get_topics

class TopicsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_qos = 0  # Default QoS level

        ttk.Label(self, text="Discovered Topics", font=("Arial", 16)).pack(pady=10)

        # Treeview for Topics
        self.topic_listbox = ttk.Treeview(self, columns=("Topics"), show="tree")
        self.topic_listbox.pack(pady=10, fill="both", expand=True)
        self.view_button = ttk.Button(self, text="View Topic Data", bootstyle="primary", command=self.view_topic_data)
        self.view_button.pack(pady=5)
        # QoS Selection Buttons
        ttk.Label(self, text="Change QoS Level:").pack(pady=5)

        qos_buttons_frame = ttk.Frame(self)
        qos_buttons_frame.pack(pady=5)

        ttk.Button(qos_buttons_frame, text="QoS 0", bootstyle="info", command=lambda: self.change_qos(0)).pack(side="left", padx=5)
        ttk.Button(qos_buttons_frame, text="QoS 1", bootstyle="warning", command=lambda: self.change_qos(1)).pack(side="left", padx=5)
        ttk.Button(qos_buttons_frame, text="QoS 2", bootstyle="danger", command=lambda: self.change_qos(2)).pack(side="left", padx=5)

        # Load Topics
        self.load_topics()

        # Initial subscription to all topics
        self.subscribe_to_all(self.current_qos)

    def load_topics(self):
        """Load topics from the database into the Treeview."""
        topics = get_topics()
        for topic in topics:
            self.topic_listbox.insert("", "end", text=topic)

    def subscribe_to_all(self, qos):
        """Subscribe to all topics with the given QoS level."""
        mqtt_client.subscribe("#", self.on_new_message, qos)
        print(f"[INFO] Subscribed to all topics with QoS {qos}")

    def change_qos(self, qos):
        """Unsubscribe and resubscribe to all topics with a new QoS level."""
        if qos != self.current_qos:
            mqtt_client.subscribe("#", self.on_new_message, qos)  # Triggers resubscription
            self.current_qos = qos
            print(f"[INFO] Changed QoS level to {qos}")

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
    
    def view_topic_data(self):
        """Open the selected topic's data page."""
        selected_item = self.topic_listbox.selection()
        if selected_item:
            topic = self.topic_listbox.item(selected_item, "text")
            topic_frame = self.controller.frames["TopicDataPage"]
            topic_frame.set_topic(topic)
            self.controller.show_frame("TopicDataPage")
        else:
            print("[WARNING] No topic selected.")

