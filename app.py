import streamlit as st
import pandas as pd
import time
import random
import matplotlib.pyplot as plt

# Load Dataset
df = pd.read_csv("multi_cloud_dataset_10000.csv")

# Convert IP to numeric
def ip_to_numeric(ip):
    parts = ip.split(".")
    return int(parts[0])*256**3 + int(parts[1])*256**2 + int(parts[2])*256 + int(parts[3])

df["sourceIP"] = df["sourceIP"].apply(ip_to_numeric)

# Encode categorical columns
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

# Dummy Prediction Function
def predict_event(sample):
    score = round(random.uniform(0, 1), 3)

    if score < 0.4:
        decision = "ALLOW"
    elif score < 0.7:
        decision = "MFA REQUIRED"
    else:
        decision = "BLOCK"

    return score, decision

# Streamlit UI
st.set_page_config(page_title="Cloud Security Dashboard", layout="wide")

st.title(" Cognitive Multi-Cloud Security Dashboard")

# Sidebar
st.sidebar.header("Controls")
run = st.sidebar.checkbox("Start Live Monitoring")

block_count = 0
mfa_count = 0

table_placeholder = st.empty()
chart_placeholder = st.empty()

scores = []
data_table = []

# Live Simulation
if run:
    for i in range(50):
        sample = X.sample(1).iloc[0].to_dict()

        score, decision = predict_event(sample)

        if decision == "BLOCK":
            block_count += 1
        elif decision == "MFA REQUIRED":
            mfa_count += 1

        data_table.append({
            "Risk Score": score,
            "Decision": decision
        })

        scores.append(score)

        df_display = pd.DataFrame(data_table)
        table_placeholder.dataframe(df_display)

        st.sidebar.metric(" BLOCK", block_count)
        st.sidebar.metric(" MFA", mfa_count)

        fig, ax = plt.subplots()
        ax.plot(scores)
        ax.set_title("Risk Score Trend")
        chart_placeholder.pyplot(fig)

        time.sleep(1)