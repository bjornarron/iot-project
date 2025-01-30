import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.database import get_data_for_topic

class TopicDataPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.topic = None

        self.label = ttk.Label(self, text="Select a Topic", font=("Arial", 16))
        self.label.pack(pady=10)

        self.data_box = ttk.ScrolledText(self, width=50, height=15)
        self.data_box.pack(pady=10)

        ttk.Button(self, text="Back to Topics", bootstyle="secondary", command=lambda: controller.show_frame("TopicsPage")).pack(pady=10)

    def set_topic(self, topic):
        """Set the topic and display its data."""
        self.topic = topic
        self.label.config(text=f"Data for {self.topic}")
        self.load_data()

    def load_data(self):
        """Load data for the current topic into the data box."""
        self.data_box.delete("1.0", "end")
        data = get_data_for_topic(self.topic)
        for entry in data:
            self.data_box.insert("end", f"{entry[1]}: {entry[0]}\n")
