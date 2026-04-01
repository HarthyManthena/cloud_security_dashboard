import joblib
import pandas as pd
from policy_engine import enforce_policy

# Load model
rf = joblib.load("random_forest_model.pkl")

# Load one sample
df = pd.read_csv("access_control_dataset.csv")
sample = df.sample(1)

# Convert bool to int
bool_columns = sample.select_dtypes(include=['bool']).columns
sample[bool_columns] = sample[bool_columns].astype(int)

# Create Security Score
score = sample[bool_columns].sum(axis=1).values[0]

# Encode categorical
sample = pd.get_dummies(sample)
sample = sample.reindex(columns=rf.feature_names_in_, fill_value=0)

prediction = rf.predict(sample)[0]
confidence = max(rf.predict_proba(sample)[0])

print("Security Score:", score)
print("Risk Level:", "High Risk" if prediction == 1 else "Low Risk")
print("Confidence:", round(confidence, 2))
print("Policy Decision:", enforce_policy(prediction, score))