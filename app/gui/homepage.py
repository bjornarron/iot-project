import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Welcome to Smart Home MQTT", font=("Arial", 16)).pack(pady=20)

        ttk.Label(self, text="Use the navigation bar above to switch between pages.", font=("Arial", 12)).pack(pady=10)
