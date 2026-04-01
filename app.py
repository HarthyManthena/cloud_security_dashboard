import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import random

# PAGE CONFIG
st.set_page_config(page_title="Multi-Cloud Security", layout="wide")


# LOGIN SYSTEM
def login():
    st.title(" Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["login"] = True
        else:
            st.error("Invalid Credentials")

if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    login()
    st.stop()

# AWS STYLE UI
st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    .stMetric {background-color:#1c1f26; padding:10px; border-radius:10px;}
    </style>
""", unsafe_allow_html=True)

st.title(" Multi-Cloud Security ")

# LOAD MODELS & DATA
@st.cache_resource
def load_models():
    rf_model = joblib.load("rf_model.pkl")
    svm_model = joblib.load("svm_model.pkl")
    iso_model = joblib.load("iso_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return rf_model, svm_model, iso_model, scaler

rf_model, svm_model, iso_model, scaler = load_models()

@st.cache_data
def load_data():
    return pd.read_csv("multi_cloud_dataset_10000.csv")

rf_model, svm_model, iso_model, scaler = load_models()
df = load_data()

# PREDICTION FUNCTION
def predict_event(features, rf_model, svm_model, iso_model, scaler):
    import numpy as np

    features = scaler.transform([features])

    # RF
    rf_score = rf_model.predict_proba(features)[0][1]

    # SVM
    try:
        svm_score = svm_model.predict_proba(features)[0][1]
    except:
        svm_score = svm_model.decision_function(features)[0]
        svm_score = 1 / (1 + np.exp(-svm_score))

    # Isolation Forest
    iso_score = iso_model.decision_function(features)[0]
    iso_score = (iso_score + 1) / 2

    # Final Score
    import random

    base_score = (rf_score + svm_score + iso_score) / 3

    # Add randomness
    noise = random.uniform(-0.3, 0.3)
    final_score = base_score + noise

    # Clamp between 0 and 1
    final_score = max(0, min(1, final_score))

    if final_score < 0.4:
        decision = "ALLOW"
    elif final_score < 0.7:
        decision = "MFA REQUIRED"
    else:
        decision = "BLOCK"

    return final_score, decision

# SIDEBAR CONTROLS
st.sidebar.header(" Controls")
num_events = st.sidebar.slider("Events", 5, 50, 15)

# KPI VARIABLES
total = 0
blocked = 0
mfa = 0
allowed = 0

results = []

# LIVE SIMULATION
st.subheader(" Live Security Events")

for i in range(num_events):
    row_df = df.sample(1).drop("label", axis=1)

    # Convert categorical → numeric
    row_df = row_df.apply(lambda x: pd.factorize(x)[0])

    row = row_df.values[0]

    score, decision = predict_event(row, rf_model, svm_model, iso_model, scaler)

    total += 1
    if decision == "BLOCK":
        blocked += 1
        st.error(f" HIGH RISK detected (Score: {round(score,2)})")
    elif decision == "MFA REQUIRED":
        mfa += 1
        st.warning(f" Medium Risk (Score: {round(score,2)})")
    else:
        allowed += 1

    results.append({
        "Event": i+1,
        "Risk Score": round(score, 2),
        "Decision": decision,
        "Latitude": random.uniform(-90, 90),
        "Longitude": random.uniform(-180, 180)
    })

# KPI DASHBOARD
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", total)
col2.metric("Blocked", blocked)
col3.metric("MFA", mfa)
col4.metric("Allowed", allowed)

result_df = pd.DataFrame(results)

# TABLE
st.dataframe(result_df, use_container_width=True)

# PIE CHART
st.subheader(" Decision Distribution")

fig1 = px.pie(result_df, names="Decision")
st.plotly_chart(fig1, use_container_width=True)

# TIME SERIES GRAPH
st.subheader(" Risk Trend Over Time")

fig2 = px.line(result_df, x="Event", y="Risk Score")
st.plotly_chart(fig2, use_container_width=True)

# ATTACK MAP
st.subheader(" Attack Location Map")

map_df = result_df.rename(columns={
    "Latitude": "lat",
    "Longitude": "lon"
})[["lat", "lon"]]

st.map(map_df)

# DOWNLOAD REPORT
csv = result_df.to_csv(index=False)

st.download_button(
    label=" Download Report",
    data=csv,
    file_name="security_report.csv",
    mime="text/csv"
)

# REFRESH
if st.button(" Refresh Dashboard"):
    st.rerun()