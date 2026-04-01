import tkinter as tk
from tkinter import ttk
import pandas as pd
import joblib
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load Models
rf = joblib.load("rf_model.pkl")
svm = joblib.load("svm_model.pkl")
iso = joblib.load("iso_model.pkl")
scaler = joblib.load("scaler.pkl")

df = pd.read_csv("multi_cloud_dataset_10000.csv")

# Convert IP
def ip_to_numeric(ip):
    parts = ip.split(".")
    return int(parts[0])*256**3 + int(parts[1])*256**2 + int(parts[2])*256 + int(parts[3])

df["sourceIP"] = df["sourceIP"].apply(ip_to_numeric)

# Encode
from sklearn.preprocessing import LabelEncoder

le_event = LabelEncoder()
le_region = LabelEncoder()
le_user = LabelEncoder()
le_cloud = LabelEncoder()

df["eventName"] = le_event.fit_transform(df["eventName"])
df["region"] = le_region.fit_transform(df["region"])
df["userType"] = le_user.fit_transform(df["userType"])
df["cloudProvider"] = le_cloud.fit_transform(df["cloudProvider"])

df["label"] = df["label"].map({"Normal": 0, "Suspicious": 1})

X = df.drop("label", axis=1)

# Cognitive Engine
def predict_event(sample):
    sample_df = pd.DataFrame([sample])
    sample_scaled = scaler.transform(sample_df)

    rf_score = rf.predict_proba(sample_df)[0][1]
    svm_score = svm.predict_proba(sample_scaled)[0][1]
    iso_score = iso.decision_function(sample_df)[0]
    iso_score = 1 - (iso_score + 0.5)

    final_score = (rf_score + svm_score + iso_score) / 3

    if final_score < 0.4:
        decision = "ALLOW"
        color = "green"
    elif final_score < 0.7:
        decision = "MFA"
        color = "orange"
    else:
        decision = "BLOCK"
        color = "red"

    return round(final_score, 3), decision, color

# GUI Setup
root = tk.Tk()
root.title("Advanced Cloud Security Dashboard")
root.geometry("900x600")

title = tk.Label(root, text=" Cognitive Multi-Cloud Security Dashboard", font=("Arial", 18))
title.pack(pady=10)

# Table
table = ttk.Treeview(root, columns=("Score", "Decision"), show="headings", height=10)
table.heading("Score", text="Risk Score")
table.heading("Decision", text="Decision")
table.pack(pady=10)

# Counters
block_count = 0
mfa_count = 0

counter_label = tk.Label(root, text="BLOCK: 0 | MFA: 0", font=("Arial", 12))
counter_label.pack()

# Graph setup
scores = []

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Live Event Generator
def generate_event():
    global block_count, mfa_count

    sample = X.sample(1).iloc[0].to_dict()
    score, decision, color = predict_event(sample)

    table.insert("", "end", values=(score, decision), tags=(color,))
    table.tag_configure("red", background="#ff4d4d")
    table.tag_configure("orange", background="#ffcc00")
    table.tag_configure("green", background="#99ff99")

    # Update counters
    if decision == "BLOCK":
        block_count += 1
    elif decision == "MFA":
        mfa_count += 1

    counter_label.config(text=f"BLOCK: {block_count} | MFA: {mfa_count}")

    # Update graph
    scores.append(score)
    ax.clear()
    ax.plot(scores)
    ax.set_title("Risk Score Trend")
    canvas.draw()

    # Auto-run every 2 seconds
    root.after(2000, generate_event)

# Start button
start_btn = tk.Button(root, text="Start Monitoring", command=generate_event)
start_btn.pack(pady=10)

# Run GUI
root.mainloop()