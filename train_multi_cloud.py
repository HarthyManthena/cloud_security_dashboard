import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Load Dataset
df = pd.read_csv("multi_cloud_dataset_10000.csv")

print(" Dataset Loaded Successfully")

# Convert IP Address to Numeric
def ip_to_numeric(ip):
    try:
        parts = ip.split(".")
        return int(parts[0])*256**3 + int(parts[1])*256**2 + int(parts[2])*256 + int(parts[3])
    except:
        return 0

df["sourceIP"] = df["sourceIP"].apply(ip_to_numeric)

print(" IP Address Converted Successfully")

# Encode Categorical Features
le_event = LabelEncoder()
le_region = LabelEncoder()
le_user = LabelEncoder()
le_cloud = LabelEncoder()

df["eventName"] = le_event.fit_transform(df["eventName"])
df["region"] = le_region.fit_transform(df["region"])
df["userType"] = le_user.fit_transform(df["userType"])
df["cloudProvider"] = le_cloud.fit_transform(df["cloudProvider"])

# Convert label to numeric
df["label"] = df["label"].map({"Normal": 0, "Suspicious": 1})

print(" Encoding Completed")

# Features & Target
X = df.drop("label", axis=1)
y = df["label"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(" Data Split Done")

# Scaling (for SVM)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Models
print("\n Training Models\n")

# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

print(" Random Forest Trained")

# SVM
svm = SVC(probability=True)
svm.fit(X_train_scaled, y_train)

print(" SVM Trained")

# Isolation Forest
iso = IsolationForest(contamination=0.5)
iso.fit(X_train)

print(" Isolation Forest Trained")

print("\n ALL MODELS TRAINED SUCCESSFULLY")

# Save Models
joblib.dump(rf, "rf_model.pkl")
joblib.dump(svm, "svm_model.pkl")
joblib.dump(iso, "iso_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\n Models Saved Successfully")

# Cognitive Risk Engine
def cognitive_risk_engine(sample):
    sample_df = pd.DataFrame([sample])

    # Scale for SVM
    sample_scaled = scaler.transform(sample_df)

    # RF Score
    rf_score = rf.predict_proba(sample_df)[0][1]

    # SVM Score
    svm_score = svm.predict_proba(sample_scaled)[0][1]

    # Isolation Forest Score
    iso_score = iso.decision_function(sample_df)[0]
    iso_score = 1 - (iso_score + 0.5)

    # Final Score
    final_score = (rf_score + svm_score + iso_score) / 3

    # Decision Logic
    if final_score < 0.4:
        decision = "ALLOW"
    elif final_score < 0.7:
        decision = "MFA REQUIRED"
    else:
        decision = "BLOCK"

    return {
        "Final Score": round(final_score, 3),
        "Decision": decision
    }

# Test Live Simulation
print("\n Testing Real-Time Simulation\n")

for i in range(5):
    sample = X_test.sample(1).iloc[0].to_dict()
    result = cognitive_risk_engine(sample)

    print(f"Event {i+1}: {result}")

print("\n SYSTEM READY FOR DEPLOYMENT")