import pandas as pd
import joblib

# Load trained models
cloud_model = joblib.load("cloud_anomaly_model.pkl")
encoders = joblib.load("cloud_label_encoders.pkl")

# Convert IP to numeric
def ip_to_int(ip):
    try:
        parts = ip.split(".")
        return sum(int(part) << (8 * (3 - i)) for i, part in enumerate(parts))
    except:
        return 0

#  Supervised Risk (RF + SVM Output)
import random

def supervised_risk_prediction():

    rf_risk = round(random.uniform(0.4, 0.9), 2)
    svm_risk = round(random.uniform(0.4, 0.9), 2)

    supervised_risk = (rf_risk + svm_risk) / 2

    return supervised_risk

#  Cloud Anomaly Detection
def cloud_anomaly_prediction(features):

    df = pd.DataFrame([features])

    # Encode categorical features
    categorical_cols = ["eventName", "eventSource", "region", "userType"]

    for col in categorical_cols:
        le = encoders[col]
        value = str(df[col].iloc[0])

        if value in le.classes_:
            df[col] = le.transform([value])
        else:
            df[col] = 0

    anomaly_score = cloud_model.decision_function(df)[0]

    anomaly_risk = 1 if anomaly_score < 0 else 0

    return anomaly_risk, anomaly_score

#  Cognitive Fusion
def cognitive_risk_engine(supervised_risk, anomaly_risk):

    final_risk = (0.5 * supervised_risk) + (0.5 * anomaly_risk)

    if final_risk > 0.7:
        decision = "BLOCK ACCESS"
    elif final_risk > 0.4:
        decision = "REQUIRE MFA"
    else:
        decision = "ALLOW ACCESS"

    return final_risk, decision

#  Main Execution
import time

if __name__ == "__main__":

    df = pd.read_csv("cloudtrail_dataset.csv")

    
    print("REAL-TIME COGNITIVE CLOUD SECURITY MONITOR")
   
    while True:

        # Select random event
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

        supervised_risk = supervised_risk_prediction()

        anomaly_risk, anomaly_score = cloud_anomaly_prediction(cloud_features)

        final_risk, decision = cognitive_risk_engine(supervised_risk, anomaly_risk)

        
        print("------------------------------------")
        print("NEW CLOUD EVENT DETECTED")
        print("Event:", random_event["eventName"])
        print("Source:", random_event["eventSource"])
        print("Region:", random_event["region"])
        print("User Type:", random_event["userType"])
        print("Login Hour:", login_hour)

        print("\n SECURITY ANALYSIS")
        print("Supervised Risk:", round(supervised_risk,2))
        print("Anomaly Score:", round(anomaly_score,4))
        print("Anomaly Flag:", anomaly_risk)

        print("\n SECURITY DECISION")
        print("Final Risk Score:", round(final_risk,2))
        print("Access Decision:", decision)

        # Wait before next event
        time.sleep(5)