import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import numpy as np
import seaborn as sns
import pandas as pd
from app.database import get_qos_latency_data, get_qos_comparison, get_latency_dataframe


class GraphsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="QoS Performance Graphs", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self, text="Latency Over Time", bootstyle="primary", command=self.show_latency_graph).pack(pady=5)
        ttk.Button(self, text="Packet Size vs Latency", bootstyle="primary", command=self.show_packet_latency_graph).pack(pady=5)
        ttk.Button(self, text="Jitter Over Time", bootstyle="primary", command=self.show_jitter_graph).pack(pady=5)
        ttk.Button(self, text="QoS Comparison", bootstyle="success", command=self.show_qos_comparison_graph).pack(pady=5)
        ttk.Button(self, text="Latency Histogram", bootstyle="info", command=self.show_latency_histogram).pack(pady=5)
        ttk.Button(self, text="Latency Boxplot", bootstyle="info", command=self.show_latency_boxplot).pack(pady=5)
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

        plt.close(fig)
        
    def show_latency_graph(self):
        """Latency over time comparison with better separation for QoS levels."""
        data = get_qos_latency_data()
        if not data:
            print("[DEBUG] No latency data available.")
            return

        qos_levels, latencies, _, _ = zip(*data)

        # Organize data by QoS level
        latency_data = {0: [], 1: [], 2: []}
        time_index = {0: [], 1: [], 2: []}
        message_count = {0: 0, 1: 0, 2: 0}

        for i, (qos, latency) in enumerate(zip(qos_levels, latencies)):
            if qos in latency_data and latency is not None:
                latency_data[qos].append(latency)
                time_index[qos].append(message_count[qos])  # X-axis is message index
                message_count[qos] += 1

        # Calculate average latency per QoS
        avg_latency = {qos: np.mean(latency_data[qos]) if latency_data[qos] else None for qos in latency_data}

        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))

        colors = {0: "blue", 1: "green", 2: "red"}
        labels = {0: "QoS 0", 1: "QoS 1", 2: "QoS 2"}

        # Plot latency for each QoS
        for qos in latency_data:
            if latency_data[qos]:
                ax.plot(time_index[qos], latency_data[qos], marker="o", linestyle="-", color=colors[qos], label=f"{labels[qos]} (Avg: {avg_latency[qos]:.3f} sec)")

        ax.set_xlabel("Message Index (Time)")
        ax.set_ylabel("Latency (Seconds)")
        ax.set_title("Latency Over Time for Different QoS Levels")
        ax.legend(loc="upper left")
        ax.grid(True)

        # Embed graph into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close(fig)

                
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

        plt.close(fig)

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

        plt.close(fig)
        
    def display_graph(self, fig):
        """Clear previous graph and display a new one."""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        plt.close(fig)


    def show_latency_histogram(self):
        """Plot histogram of latency distributions per QoS level."""
        df = get_latency_dataframe()
        if df.empty:
            ttk.Label(self.graph_frame, text="No Data Available", font=("Arial", 14), foreground="red").pack()
            return

        qos_levels = sorted(df["qos_level"].unique())
        latency_data = [df[df["qos_level"] == qos]["latency"] for qos in qos_levels]

        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ["blue", "green", "red"]
        labels = [f"QoS {q}" for q in qos_levels]

        for data, color, label in zip(latency_data, colors, labels):
            ax.hist(data, bins=30, alpha=0.5, label=label, color=color, edgecolor="black")

        ax.set_title("Latency Distribution per QoS Level")
        ax.set_xlabel("Latency (seconds)")
        ax.set_ylabel("Frequency")
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)


    def show_latency_boxplot(self):
        """Boxplot of latency values per QoS level."""
        df = get_latency_dataframe()
        if df.empty:
            ttk.Label(self.graph_frame, text="No Data Available", font=("Arial", 14), foreground="red").pack()
            return

        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 5))
        sns.boxplot(x="qos_level", y="latency", data=df, palette=["blue", "green", "red"], ax=ax)

        ax.set_title("Latency Boxplot per QoS Level")
        ax.set_xlabel("QoS Level")
        ax.set_ylabel("Latency (seconds)")
        ax.yaxis.set_major_locator(ticker.MaxNLocator(10))
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
