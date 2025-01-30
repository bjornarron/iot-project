import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.mqtt_client import mqtt_client

class CommandPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Send Commands", font=("Arial", 16)).pack(pady=20)

        self.command_entry = ttk.Entry(self, width=40)
        self.command_entry.pack(pady=5)
        ttk.Button(self, text="Send Command", bootstyle="success", command=self.send_command).pack(pady=5)

    def send_command(self):
        """Publishes a command message to the MQTT broker."""
        command = self.command_entry.get()
        if command:
            mqtt_client.publish("home/commands", command)
            self.command_entry.delete(0, ttk.END)
