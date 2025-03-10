import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import numpy as np
from app.database import get_qos_latency_data, get_qos_comparison


class GraphsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="QoS Performance Graphs", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self, text="Latency Over Time", bootstyle="primary", command=self.show_latency_graph).pack(pady=5)
        ttk.Button(self, text="Packet Size vs Latency", bootstyle="primary", command=self.show_packet_latency_graph).pack(pady=5)
        ttk.Button(self, text="Jitter Over Time", bootstyle="primary", command=self.show_jitter_graph).pack(pady=5)
        ttk.Button(self, text="QoS Comparison", bootstyle="success", command=self.show_qos_comparison_graph).pack(pady=5)
        ttk.Button(self, text="Back to Home", bootstyle="secondary", command=lambda: controller.show_frame("HomePage")).pack(pady=10)

        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def show_packet_latency_graph(self):
        """Packet Size vs Latency comparison for each QoS level."""
        data = get_qos_latency_data()
        if not data:
            print("[DEBUG] No data to display")
            ttk.Label(self.graph_frame, text="No Data Available", font=("Arial", 14), foreground="red").pack()
            return

        qos_levels, latencies, packet_sizes, _ = zip(*data)

        # Organize data by QoS
        qos_data = {0: [], 1: [], 2: []}
        packet_data = {0: [], 1: [], 2: []}

        for qos, latency, packet_size in zip(qos_levels, latencies, packet_sizes):
            qos_data[qos].append(latency)
            packet_data[qos].append(packet_size)

        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 5))

        colors = {0: "blue", 1: "green", 2: "red"}
        labels = {0: "QoS 0", 1: "QoS 1", 2: "QoS 2"}

        # Plot latency vs packet size for each QoS
        for qos in qos_data:
            if qos_data[qos]:
                ax.scatter(packet_data[qos], qos_data[qos], color=colors[qos], alpha=0.5, label=labels[qos])

        ax.set_xlabel("Packet Size (Bytes)")
        ax.set_ylabel("Avg Latency (Seconds)")
        ax.set_title("Latency vs Packet Size per QoS Level")
        ax.legend()
        ax.grid(True)

        # Embed graph into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        
    def show_latency_graph(self):
        """Latency over time comparison for QoS 0, 1, and 2."""
        data = get_qos_latency_data()
        if not data:
            print("[DEBUG] No latency data available.")
            return

        qos_levels, latencies, _, _ = zip(*data)

        # Organize data by QoS level
        latency_data = {0: [], 1: [], 2: []}
        time_index = {0: [], 1: [], 2: []}

        for i, (qos, latency) in enumerate(zip(qos_levels, latencies)):
            latency_data[qos].append(latency)
            time_index[qos].append(i)  # X-axis is message index

        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 5))

        colors = {0: "blue", 1: "green", 2: "red"}
        labels = {0: "QoS 0", 1: "QoS 1", 2: "QoS 2"}

        # Plot latency for each QoS
        for qos in latency_data:
            if latency_data[qos]:
                ax.plot(time_index[qos], latency_data[qos], marker="o", linestyle="-", color=colors[qos], label=labels[qos])

        ax.set_xlabel("Message Index (Time)")
        ax.set_ylabel("Latency (Seconds)")
        ax.set_title("Latency Over Time for Different QoS Levels")
        ax.legend()
        ax.grid(True)

        # Embed graph into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def show_jitter_graph(self):
        """Jitter over time comparison per QoS level."""
        data = get_qos_latency_data()
        if not data:
            print("[DEBUG] No jitter data available.")
            return

        qos_levels, _, _, jitters = zip(*data)

        # Organize data by QoS level
        jitter_data = {0: [], 1: [], 2: []}
        time_index = {0: [], 1: [], 2: []}

        for i, (qos, jitter) in enumerate(zip(qos_levels, jitters)):
            jitter_data[qos].append(jitter)
            time_index[qos].append(i)  # X-axis is message index

        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Create figure
        fig, ax = plt.subplots(figsize=(7, 5))

        colors = {0: "blue", 1: "green", 2: "red"}
        labels = {0: "QoS 0", 1: "QoS 1", 2: "QoS 2"}

        # Plot jitter for each QoS
        for qos in jitter_data:
            if jitter_data[qos]:
                ax.plot(time_index[qos], jitter_data[qos], marker="o", linestyle="-", color=colors[qos], label=labels[qos])

        ax.set_xlabel("Message Index (Time)")
        ax.set_ylabel("Jitter (Seconds)")
        ax.set_title("Jitter Over Time for Different QoS Levels")
        ax.legend()
        ax.grid(True)

        # Embed graph into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def show_qos_comparison_graph(self):
        """Compare received packet count per QoS level including retransmissions."""
        data = get_qos_comparison()
        if not data:
            print("[DEBUG] No QoS comparison data available.")
            ttk.Label(self.graph_frame, text="No Data Available", font=("Arial", 14), foreground="red").pack()
            return

        qos_levels, packet_counts = zip(*data)

        fig, ax = plt.subplots(figsize=(6, 4))
        
        colors = ["red", "blue", "green"]
        labels = ["QoS 0", "QoS 1 (Retransmissions Included)", "QoS 2"]
        
        ax.bar(qos_levels, packet_counts, color=colors, alpha=0.7)

        ax.set_xlabel("QoS Level")
        ax.set_ylabel("Packets Received (Including Retransmissions)")
        ax.set_title("MQTT QoS Packet Delivery Comparison")
        ax.set_xticks(qos_levels)
        ax.set_xticklabels(labels)
        ax.grid(True)

        self.display_graph(fig)


    def display_graph(self, fig):
        """Clear previous graph and display a new one."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
