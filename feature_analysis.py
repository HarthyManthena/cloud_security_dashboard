import pandas as pd
import joblib
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("access_control_dataset.csv")

# Convert bool to int
bool_columns = df.select_dtypes(include=['bool']).columns
df[bool_columns] = df[bool_columns].astype(int)

# Encode categorical
df = pd.get_dummies(df)

# Load trained model
rf = joblib.load("random_forest_model_2.pkl")

# Get feature importance
importances = rf.feature_importances_
features = df.columns[:len(importances)]

# Create importance dataframe
importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\nTop 10 Important Features:")
print(importance_df.head(10))

# Plot
plt.figure()
plt.barh(importance_df["Feature"].head(10), 
         importance_df["Importance"].head(10))
plt.xlabel("Importance Score")
plt.title("Top 10 Important Security Features")
plt.gca().invert_yaxis()
plt.show()