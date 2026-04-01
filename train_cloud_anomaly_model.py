import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import joblib
import numpy as np

# Load dataset
df = pd.read_csv("cloudtrail_dataset.csv")

# Drop rows with missing eventTime
df = df.dropna(subset=["eventTime"])

# Convert time
df["eventTime"] = pd.to_datetime(df["eventTime"])

# Feature 1: Hour of login/API call
df["login_hour"] = df["eventTime"].dt.hour

# Feature 2: MFA flag
df["mfa_flag"] = df["mfaUsed"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

# Feature 3: Encode categorical features
categorical_cols = ["eventName", "eventSource", "region", "userType"]

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

# Feature 4: Convert IP to numeric (simple method)
def ip_to_int(ip):
    try:
        parts = ip.split(".")
        return sum(int(part) << (8 * (3 - i)) for i, part in enumerate(parts))
    except:
        return 0

df["ip_numeric"] = df["sourceIP"].apply(ip_to_int)

# Select final features
features = [
    "login_hour",
    "mfa_flag",
    "eventName",
    "eventSource",
    "region",
    "userType",
    "ip_numeric"
]

X = df[features]

# Train Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42
)

model.fit(X)

# Save model
joblib.dump(model, "cloud_anomaly_model.pkl")
joblib.dump(encoders, "cloud_label_encoders.pkl")

print(" Cloud Anomaly Model Trained and Saved Successfully!")