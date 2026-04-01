import pandas as pd
import joblib
import numpy as np

# Load trained model and encoders
model = joblib.load("cloud_anomaly_model.pkl")
encoders = joblib.load("cloud_label_encoders.pkl")

def ip_to_int(ip):
    try:
        parts = ip.split(".")
        return sum(int(part) << (8 * (3 - i)) for i, part in enumerate(parts))
    except:
        return 0

def predict_cloud_event(event_dict):

    # Convert to DataFrame
    df = pd.DataFrame([event_dict])

    # Convert time
    df["eventTime"] = pd.to_datetime(df["eventTime"])
    df["login_hour"] = df["eventTime"].dt.hour

    # MFA flag
    df["mfa_flag"] = df["mfaUsed"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

    # Encode categorical columns
    categorical_cols = ["eventName", "eventSource", "region", "userType"]

    for col in categorical_cols:
        le = encoders[col]
 
        value = str(df[col].iloc[0])

        if value in le.classes_:
            df[col] = le.transform([value])
        else:
            # Unknown category → assign default value
            df[col] = 0

    # Convert IP
    df["ip_numeric"] = df["sourceIP"].apply(ip_to_int)

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

    prediction = model.predict(X)[0]
    anomaly_score = model.decision_function(X)[0]

    anomaly_flag = 1 if prediction == -1 else 0

    return {
        "anomaly_flag": anomaly_flag,
        "anomaly_score": float(anomaly_score)
    }


#  Test with one sample event from your dataset
if __name__ == "__main__":

    df = pd.read_csv("cloudtrail_dataset.csv")

    for i in range(5):
        event = df.iloc[i].to_dict()
        result = predict_cloud_event(event)
        print("Prediction Result:")
        print(result)
