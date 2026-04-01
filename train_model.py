# BASELINE MODEL (Deterministic Risk Label)
# Used for experimental comparison
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Load dataset
df = pd.read_csv("access_control_dataset.csv")

print("Dataset Loaded Successfully")
print("Shape:", df.shape)

# Convert boolean columns to int
bool_columns = df.select_dtypes(include=['bool']).columns
df[bool_columns] = df[bool_columns].astype(int)

# Encode categorical columns
cat_columns = df.select_dtypes(include=['object']).columns
le_dict = {}

for col in cat_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    le_dict[col] = le

# -----------------------------
# CREATE SECURITY SCORE
# -----------------------------

df['Security_Score'] = df[bool_columns].sum(axis=1)

threshold = df['Security_Score'].median()

df['Risk_Label'] = df['Security_Score'].apply(
    lambda x: 1 if x < threshold else 0
)

# 1 = High Risk
# 0 = Low Risk

X = df.drop(['Security_Score', 'Risk_Label'], axis=1)
y = df['Risk_Label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# RANDOM FOREST
# -----------------------------

rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

print("\nRandom Forest Results:")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print(confusion_matrix(y_test, rf_pred))
print(classification_report(y_test, rf_pred))

# -----------------------------
# SVM
# -----------------------------

svm = SVC()
svm.fit(X_train, y_train)

svm_pred = svm.predict(X_test)

print("\nSVM Results:")
print("Accuracy:", accuracy_score(y_test, svm_pred))
print(confusion_matrix(y_test, svm_pred))
print(classification_report(y_test, svm_pred))

# Save models
joblib.dump(rf, "random_forest_model.pkl")
joblib.dump(svm, "svm_model.pkl")

print("\nModels saved successfully.")