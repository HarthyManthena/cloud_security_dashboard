import streamlit as st
import pandas as pd
import time
import random
import matplotlib.pyplot as plt

# PAGE CONFIG
st.set_page_config(page_title="Cloud Security SOC", layout="wide")

# CUSTOM CSS (Dark SOC Style)
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .metric-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #1c1f26;
        text-align: center;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# TITLE
st.title(" Cognitive Multi-Cloud Security Dashboard")

# LOAD DATA
df = pd.read_csv("multi_cloud_dataset_10000.csv")

# SIDEBAR
st.sidebar.header(" Control Panel")
run = st.sidebar.checkbox("Start Monitoring")

# KPI counters
block_count = 0
mfa_count = 0
allow_count = 0

# placeholders
table_placeholder = st.empty()
chart_placeholder = st.empty()

scores = []
data_table = []

# DUMMY PREDICTION
def predict_event():
    score = round(random.uniform(0, 1), 3)

    if score < 0.4:
        decision = "ALLOW"
    elif score < 0.7:
        decision = "MFA REQUIRED"
    else:
        decision = "BLOCK"

    return score, decision

# KPI SECTION
col1, col2, col3 = st.columns(3)

block_metric = col1.empty()
mfa_metric = col2.empty()
allow_metric = col3.empty()

# LIVE SIMULATION
if run:
    for i in range(50):

        score, decision = predict_event()

        if decision == "BLOCK":
            block_count += 1
        elif decision == "MFA REQUIRED":
            mfa_count += 1
        else:
            allow_count += 1

        # Update table
        data_table.append({
            "Event ID": i+1,
            "Risk Score": score,
            "Decision": decision
        })

        df_display = pd.DataFrame(data_table)
        table_placeholder.dataframe(df_display, use_container_width=True)

        # Update KPIs
        block_metric.metric(" BLOCKED", block_count)
        mfa_metric.metric(" MFA REQUIRED", mfa_count)
        allow_metric.metric(" ALLOWED", allow_count)

        # Risk trend chart
        scores.append(score)

        fig, ax = plt.subplots()
        ax.plot(scores)
        ax.set_title(" Risk Score Trend")
        ax.set_xlabel("Events")
        ax.set_ylabel("Risk Score")
        chart_placeholder.pyplot(fig)

        # Alert system
        if decision == "BLOCK":
            st.error(f" High Risk Activity Detected! Score: {score}")
        elif decision == "MFA REQUIRED":
            st.warning(f" Medium Risk - MFA Required (Score: {score})")

        time.sleep(1)