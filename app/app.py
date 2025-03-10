import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.homepage import HomePage
from app.gui.topics import TopicsPage
from app.gui.command import CommandPage
from app.gui.topic_data import TopicDataPage
from app.mqtt_client import mqtt_client
from app.gui.graphs import GraphsPage

class MQTTApp(ttk.Window):  # Use ttkbootstrap for modern UI
    def __init__(self):
        super().__init__(themename="superhero")  # Try themes: "solar", "darkly", "flatly"

        self.title("Smart Home MQTT")
        self.geometry("800x500")  # Increased size

        # Navigation Bar
        self.navbar = ttk.Frame(self, padding=10)
        self.navbar.grid(row=0, column=0, columnspan=3, sticky="ew")

        ttk.Button(self.navbar, text="Home", command=lambda: self.show_frame("HomePage")).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="Topics", command=lambda: self.show_frame("TopicsPage")).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="Commands", command=lambda: self.show_frame("CommandPage")).pack(side="left", padx=10)
        ttk.Button(self.navbar, text="Graphs", command=lambda: self.show_frame("GraphsPage")).pack(side="left", padx=10)

        # Create Pages
        self.frames = {}
        for Page in (HomePage, TopicsPage, CommandPage, TopicDataPage, GraphsPage):
            page_name = Page.__name__
            frame = Page(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=1, column=0, sticky="nsew")

        
        self.show_frame("HomePage")

    def show_frame(self, page_name, topic=None):
        frame = self.frames[page_name]
        if page_name == "TopicDataPage" and topic:
            frame.set_topic(topic)  # Pass topic dynamically
        frame.tkraise()

if __name__ == "__main__":
    print("Starting MQTT Application")  # Debug
    app = MQTTApp()
    app.mainloop()