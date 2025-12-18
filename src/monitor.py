import sys
import os

# --- UNIVERSAL IMPORT FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__)) # Path to src/
project_root = os.path.dirname(current_dir)              # Path to Major_Project_I/
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -----------------------------

import random
import time
from datetime import datetime
from src import data_handler
from src import ai_model
from src.notify import send_alert
import re

# --- Configuration: Real Known Devices ---
# Updated with your specific hardware list
DEVICES = {
    "18:74:E2:D2:15:5D": "5G Camera (Sparsh CCTV)",
    "EC:64:C9:91:08:70": "Temp & Humidity Sensor (ESP32)",
    "30:C9:22:EF:95:88": "Water Sensor (TDS/Chlorine)",
    "EC:64:C9:91:04:5C": "Light Sensor (ESP32)",
    "D8:13:2A:30:5F:88": "Soil Sensor (NPK)",
    "B4:17:A8:DA:EB:9D": "5G XR/VR Headset (Meta Quest 3)",
    "UNKNOWN_1234": "Unknown Attacker Device"
}

# Dictionary to store the last connection time for Delta T calculation
last_connect_time = {mac: datetime.now() for mac in DEVICES.keys()}


def simulate_reconnect_delta(mac: str) -> float:
    """
    Simulates and updates the reconnect delta time.
    """
    global last_connect_time
    current_time = datetime.now()

    delta_seconds = (current_time - last_connect_time.get(mac,current_time)).total_seconds()
    last_connect_time[mac] = current_time

    # Simulate anomalous short delta T for unknown/attacker devices
    if mac == "UNKNOWN_1234":
        return random.uniform(1,10)

        # Known devices usually have stable connections (long delta)
    return random.uniform(30,300)


def simulate_traffic_features(mac: str) -> dict:
    """
    Simulates protocol, packet length, and usage based on SPECIFIC device types.
    """
    device_name = DEVICES.get(mac,"")

    if mac == "UNKNOWN_1234":
        # Attack pattern: UDP flood or Port Scan
        protocol = random.choice(['UDP','ICMP','OTHER'])
        length = random.randint(1000,1500)

    elif "Camera" in device_name:
        # Cameras usually stream video via UDP or TCP with consistent large packets
        protocol = random.choice(['UDP','TCP'])
        length = random.randint(800,1400)

    elif "VR" in device_name or "XR" in device_name:
        # VR Headsets use high bandwidth, mixed protocols
        protocol = random.choice(['UDP','TCP'])
        length = random.randint(500,1200)

    elif "Sensor" in device_name:
        # ESP32 Sensors usually send small JSON/MQTT telemetry packets
        protocol = "TCP"
        length = random.randint(40,200)  # Small payload

    else:
        # Default fallback
        protocol = 'TCP'
        length = random.randint(100,800)

    return {'protocol_type': protocol,'packet_length': length}


def simulate_log_cycle():
    """Runs one cycle of data generation, feature engineering, prediction, and storage."""

    # 1. Simulate Device Choice
    # 5% chance of simulating an unknown threat, otherwise pick a real device
    if random.random() < 0.05:
        mac_address = "UNKNOWN_1234"
    else:
        # Filter out the unknown key to pick from real devices
        real_macs = [m for m in DEVICES.keys() if m != "UNKNOWN_1234"]
        mac_address = random.choice(real_macs)

    device_name = DEVICES[mac_address]
    current_time = datetime.now()

    # 2. Feature Engineering & Simulation
    reconnect_delta = simulate_reconnect_delta(mac_address)
    hour = current_time.hour
    traffic_features = simulate_traffic_features(mac_address)

    # Usage derived from packet length and frequency (Cameras/VR use more data)
    usage = traffic_features['packet_length'] * random.randint(5,15)

    # 3. Prepare features for AI model
    features = {
        'usage': usage,
        'reconnect_delta': reconnect_delta,
        'hour': hour,
        'protocol_type': traffic_features['protocol_type'],
        'packet_length': traffic_features['packet_length'],
        'timestamp': current_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 4. Get ML Prediction
    anomaly_flag,risk_score = ai_model.predict_anomaly(features)

    # 5. Construct Final Log Entry for DB insertion
    new_log = {
        "timestamp": features['timestamp'],
        "device_mac": mac_address,
        "device_name": device_name,
        "usage": usage,
        "reconnect_delta": round(reconnect_delta,2),
        "anomaly_flag": anomaly_flag,
        "risk_score": round(risk_score,4),
        "event_group": f"WiFi/{traffic_features['protocol_type']}"
    }

    # 6. Store data in the database
    data_handler.insert_log_entry(new_log)

    print(f"Log stored: {new_log}")

    # 7. Send alert if anomaly detected
    if anomaly_flag == "YES":
        send_alert(
            f"🚨 ALERT! Unnatural Activity Detected.\nDevice: {device_name} ({mac_address})\nProtocol: {traffic_features['protocol_type']}\nRisk Score: {new_log['risk_score']}")


if __name__ == '__main__':
    print("--- Starting Edge-AI Log Monitor (Data Generation) ---")
    # Initialize DB before starting the continuous monitoring loop
    data_handler.initialize_database()
    while True:
        simulate_log_cycle()
        time.sleep(random.uniform(2,5))  # Simulate real-time collection interval