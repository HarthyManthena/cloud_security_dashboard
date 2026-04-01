import pandas as pd
import joblib
import random
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load models
cloud_model = joblib.load("cloud_anomaly_model.pkl")
encoders = joblib.load("cloud_label_encoders.pkl")

df = pd.read_csv("cloudtrail_dataset.csv")

risk_history = []
attack_locations = []

# Cognitive Threat Memory
threat_memory = set()

# IP Conversion
def ip_to_int(ip):
    try:
        parts = ip.split(".")
        return sum(int(part) << (8 * (3 - i)) for i, part in enumerate(parts))
    except:
        return 0
    
def generate_attack_location():
    # Random coordinates across the world
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    return lat, lon

# Simulated supervised risk
def supervised_risk_prediction():
    rf_risk = random.uniform(0.4, 0.9)
    svm_risk = random.uniform(0.4, 0.9)
    return (rf_risk + svm_risk) / 2

# Anomaly Detection
def cloud_anomaly_prediction(features):

    df_event = pd.DataFrame([features])

    categorical_cols = ["eventName", "eventSource", "region", "userType"]

    for col in categorical_cols:
        le = encoders[col]
        value = str(df_event[col].iloc[0])

        if value in le.classes_:
            df_event[col] = le.transform([value])
        else:
            df_event[col] = 0

    anomaly_score = cloud_model.decision_function(df_event)[0]

    anomaly_flag = 1 if anomaly_score < 0 else 0

    return anomaly_flag, anomaly_score

# Cognitive Risk Engine
def cognitive_risk_engine(supervised_risk, anomaly_risk, source_ip):

    global threat_memory

    # If IP already known as malicious
    if source_ip in threat_memory:
        final_risk = 0.95
        decision = "BLOCK ACCESS (THREAT MEMORY)"
        return final_risk, decision

    # Normal fusion
    final_risk = (0.6 * supervised_risk) + (0.4 * anomaly_risk)

    if final_risk > 0.7:
        decision = "BLOCK ACCESS"

        # Store IP in memory
        threat_memory.add(source_ip)

    elif final_risk > 0.4:
        decision = "REQUIRE MFA"

    else:
        decision = "ALLOW ACCESS"

    return final_risk, decision

# Update Graph
def update_graph():

    ax.clear()
    ax.plot(risk_history)
    ax.set_title("Risk Score Trend")
    ax.set_ylabel("Risk Score")
    ax.set_xlabel("Events")

    canvas.draw()

    # Update attacker map
    map_ax.clear()
    map_ax.set_title("Live Attack Map")
    map_ax.set_xlim(-180,180)
    map_ax.set_ylim(-90,90)
    map_ax.set_xlabel("Longitude")
    map_ax.set_ylabel("Latitude")

    if attack_locations:
        lats = [loc[0] for loc in attack_locations]
        lons = [loc[1] for loc in attack_locations]

        map_ax.scatter(lons, lats)

    map_canvas.draw()

# Real-time Simulation
suspicious_events = [
    "DeleteTrail",
    "StopLogging",
    "CreateAccessKey",
    "AuthorizeSecurityGroupIngress",
    "PutBucketPolicy",
    "DetachRolePolicy"
]

def simulate_event():

    # 30% chance of attack simulation
    attack_mode = random.random() < 0.3

    if attack_mode:

        event_name = random.choice(suspicious_events)

        random_event = df.sample(1).iloc[0]

        login_hour = random.choice([1, 2, 3, 4])   # suspicious hours
        mfa_flag = 0                               # no MFA
        ip_numeric = random.randint(1000000000, 4000000000)

        cloud_features = {
            "login_hour": login_hour,
            "mfa_flag": mfa_flag,
            "eventName": event_name,
            "eventSource": random_event["eventSource"],
            "region": random_event["region"],
            "userType": "Root",
            "ip_numeric": ip_numeric
        }

        event_display = f"{event_name}  ATTACK"

    else:

        random_event = df.sample(1).iloc[0]

        login_hour = pd.to_datetime(random_event["eventTime"]).hour
        mfa_flag = 1 if str(random_event["mfaUsed"]).lower() == "yes" else 0
        ip_numeric = ip_to_int(str(random_event["sourceIP"]))

        cloud_features = {
            "login_hour": login_hour,
            "mfa_flag": mfa_flag,
            "eventName": random_event["eventName"],
            "eventSource": random_event["eventSource"],
            "region": random_event["region"],
            "userType": random_event["userType"],
            "ip_numeric": ip_numeric
        }

        event_display = random_event["eventName"]

    supervised_risk = supervised_risk_prediction()

    anomaly_flag, anomaly_score = cloud_anomaly_prediction(cloud_features)

    final_risk, decision = cognitive_risk_engine(supervised_risk, anomaly_flag, cloud_features["ip_numeric"])

    # Security Alert System
    if final_risk > 0.7:

        status_label.config(
            text=" SECURITY ALERT: ACCESS BLOCKED",
            bg="red"
        )

        # Add attack location to map
        lat, lon = generate_attack_location()
        attack_locations.append((lat, lon))

        if len(attack_locations) > 20:
            attack_locations.pop(0)

    elif final_risk > 0.4:
        status_label.config(
            text=" SUSPICIOUS ACTIVITY: MFA REQUIRED",
            bg="orange"
        )

    else:
        status_label.config(
            text=" SYSTEM STATUS: NORMAL",
            bg="green"
        )

    risk_history.append(final_risk)

    if len(risk_history) > 20:
        risk_history.pop(0)

    event_label.config(text=f"Event: {event_display}")
    region_label.config(text=f"Region: {cloud_features['region']}")
    user_label.config(text=f"User Type: {cloud_features['userType']}")

    risk_label.config(text=f"Risk Score: {round(final_risk,2)}")
    decision_label.config(text=f"Decision: {decision}")

    if len(threat_memory) > 0:
        memory_label.config(text=f"Threat Memory IPs: {len(threat_memory)} blocked")
    else:
        memory_label.config(text="Threat Memory: None")

    update_graph()

    root.after(5000, simulate_event)

# GUI Setup
root = tk.Tk()
root.title("Cognitive Cloud Security Dashboard")
root.geometry("800x600")

title = ttk.Label(root, text="Cognitive Adaptive Cloud Security Engine", font=("Arial", 18))
title.pack(pady=10)

# Create frame FIRST
frame = ttk.Frame(root)
frame.pack()

# Status Panel
status_label = tk.Label(
    frame,
    text="SYSTEM STATUS: MONITORING",
    font=("Arial", 14, "bold"),
    bg="green",
    fg="white",
    width=40
)
status_label.pack(pady=10)

event_label = ttk.Label(frame, text="Event:")
event_label.pack()

region_label = ttk.Label(frame, text="Region:")
region_label.pack()

user_label = ttk.Label(frame, text="User Type:")
user_label.pack()

risk_label = ttk.Label(frame, text="Risk Score:", font=("Arial", 12))
risk_label.pack(pady=10)

decision_label = ttk.Label(frame, text="Decision:", font=("Arial", 14))
decision_label.pack(pady=10)

memory_label = ttk.Label(frame, text="Threat Memory: None")
memory_label.pack(pady=5)

# Graph
fig = plt.Figure(figsize=(5,3))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()

# Attack Map
map_fig = plt.Figure(figsize=(5,3))
map_ax = map_fig.add_subplot(111)

map_canvas = FigureCanvasTkAgg(map_fig, root)
map_canvas.get_tk_widget().pack()

# Start simulation
simulate_event()

root.mainloop()