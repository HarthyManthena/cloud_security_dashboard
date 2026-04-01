# FINAL ADAPTIVE MODEL (RF + SVM + Isolation Forest)
# Production Ready Version

import pandas as pd
import numpy as np
import random
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# LOAD DATASE
df = pd.read_csv("access_control_dataset.csv")

print("Dataset Loaded Successfully")
print("Shape:", df.shape)

# PREPROCESSING
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

# CREATE SECURITY SCORE
df['Security_Score'] = df[bool_columns].sum(axis=1)
threshold = df['Security_Score'].median()

def assign_risk(score):
    if score < threshold:
        return 1   # High Risk
    else:
        # Add slight randomness for realism
        return 1 if random.random() < 0.05 else 0

df['Risk_Label'] = df['Security_Score'].apply(assign_risk)

X = df.drop(['Security_Score', 'Risk_Label'], axis=1)
y = df['Risk_Label']

# Save feature column order for API use
feature_columns = X.columns.tolist()

# TRAIN TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# RANDOM FOREST
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

rf_pred_test = rf.predict(X_test)
rf_pred_train = rf.predict(X_train)

print("\n Random Forest Results")
print("Test Accuracy:", accuracy_score(y_test, rf_pred_test))
print(confusion_matrix(y_test, rf_pred_test))
print(classification_report(y_test, rf_pred_test))

print("Train Accuracy:", accuracy_score(y_train, rf_pred_train))
print(confusion_matrix(y_train, rf_pred_train))
print(classification_report(y_train, rf_pred_train))

# SVM
svm = SVC(kernel='linear')
svm.fit(X_train, y_train)

svm_pred_test = svm.predict(X_test)
svm_pred_train = svm.predict(X_train)

print("\n SVM Results ")
print("Test Accuracy:", accuracy_score(y_test, svm_pred_test))
print(confusion_matrix(y_test, svm_pred_test))
print(classification_report(y_test, svm_pred_test))

print("Train Accuracy:", accuracy_score(y_train, svm_pred_train))
print(confusion_matrix(y_train, svm_pred_train))
print(classification_report(y_train, svm_pred_train))

# ISOLATION FOREST (ANOMALY DETECTION)
iso_forest = IsolationForest(
    n_estimators=100,
    contamination=0.1,   # Assume 10% anomalies
    random_state=42
)

iso_forest.fit(X_train)

iso_pred = iso_forest.predict(X_test)

print("\n Isolation Forest Results")
print("Anomaly counts (-1 = anomaly, 1 = normal):")
print(pd.Series(iso_pred).value_counts())

# SAVE MODELS & PREPROCESSING OBJECTS
joblib.dump(rf, "random_forest_model_2.pkl")
joblib.dump(svm, "svm_model_2.pkl")
joblib.dump(iso_forest, "isolation_forest_2.pkl")
joblib.dump(le_dict, "label_encoders.pkl")
joblib.dump(feature_columns, "feature_columns.pkl")

print("\nModels and preprocessing files saved successfully.")

print("\nRisk Distribution:")
print(df['Risk_Label'].value_counts())