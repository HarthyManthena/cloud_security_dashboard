import joblib
import pandas as pd
import numpy as np
from policy_engine_2 import enforce_policy
from sklearn.ensemble import IsolationForest

# LOAD TRAINED MODELS
rf = joblib.load("random_forest_model_2.pkl")
svm = joblib.load("svm_model_2.pkl")

# LOAD DATASET
df = pd.read_csv("access_control_dataset.csv")

# Convert bool columns to int
bool_columns = df.select_dtypes(include=['bool']).columns
df[bool_columns] = df[bool_columns].astype(int)

print("\nSimulating New Cloud Configuration...\n")

# BALANCED CONFIGURATION GENERATI
sample = df.sample(1).copy()

if np.random.rand() > 0.5:
    # Strong configuration (mostly enabled controls)
    for col in bool_columns:
        sample[col] = np.random.choice([0, 1], p=[0.2, 0.8])
else:
    # Weak configuration (mostly disabled controls)
    for col in bool_columns:
        sample[col] = np.random.choice([0, 1], p=[0.7, 0.3])

# Calculate Security Score
score = sample[bool_columns].sum(axis=1).values[0]

# ENCODE SAMPLE (Match Training Features)
sample_encoded = pd.get_dummies(sample)
sample_encoded = sample_encoded.reindex(columns=rf.feature_names_in_, fill_value=0)

# ML LAYER (RF + SVM)
rf_pred = rf.predict(sample_encoded)[0]
svm_pred = svm.predict(sample_encoded)[0]

# Conservative Ensemble Voting
final_prediction = 1 if (rf_pred + svm_pred) >= 1 else 0

# Use RF probability as confidence
confidence = max(rf.predict_proba(sample_encoded)[0])

# ANOMALY DETECTION LAYER
# Train Isolation Forest on encoded dataset
df_encoded = pd.get_dummies(df)
df_encoded = df_encoded.reindex(columns=rf.feature_names_in_, fill_value=0)

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(df_encoded)

anomaly = iso.predict(sample_encoded)
is_anomaly = True if anomaly[0] == -1 else False

# If anomaly detected → escalate to High Risk
if is_anomaly:
    final_prediction = 1

# OUTPUT RESULTS
print("Security Score:", score)
print("RF Prediction:", "High Risk" if rf_pred == 1 else "Low Risk")
print("SVM Prediction:", "High Risk" if svm_pred == 1 else "Low Risk")
print("Anomaly Detected:", is_anomaly)
print("Final Ensemble Risk:", "High Risk" if final_prediction == 1 else "Low Risk")
print("Model Confidence:", round(confidence, 2))
print("Policy Enforcement Level:", enforce_policy(final_prediction, score, confidence))