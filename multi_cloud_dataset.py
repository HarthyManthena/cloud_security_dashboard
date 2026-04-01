import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker()

# Cloud-specific event lists
aws_events = ["ConsoleLogin", "ListBuckets", "CreateUser", "DeleteBucket", "AttachRolePolicy"]
azure_events = ["CreateVM", "DeleteVM", "StartVM", "StopVM", "AssignRole"]
gcp_events = ["compute.instances.create", "compute.instances.delete", "setIamPolicy", "storage.buckets.create"]

all_events = aws_events + azure_events + gcp_events

regions = ["us-east-1", "us-west-2", "eastus", "westus", "asia-south1", "europe-west1"]
user_types_normal = ["IAMUser", "Admin", "ServiceAccount"]
clouds = ["AWS", "AZURE", "GCP"]

# Suspicious IPs
suspicious_ips = ["185.220.101.1", "103.21.244.0", "45.67.89.12"]

# Generate BALANCED dataset
data = []

TOTAL_RECORDS = 10000
HALF = TOTAL_RECORDS // 2


# NORMAL EVENTS 
for i in range(HALF):
    login_hour = random.randint(6, 23)  
    user_type = random.choice(user_types_normal)

    data.append({
        "login_hour": login_hour,
        "eventName": random.choice(all_events),
        "region": random.choice(regions),
        "userType": user_type,
        "sourceIP": fake.ipv4(),
        "cloudProvider": random.choice(clouds),
        "label": "Normal"
    })

# SUSPICIOUS EVENTS 
for i in range(HALF):
    login_hour = random.randint(0, 23)
    user_type = random.choice(["Root", "Admin"])

    label = "Normal"
    ip = fake.ipv4()

    if login_hour < 6 and user_type == "Root":
        label = "Suspicious"
        ip = random.choice(suspicious_ips)
    else:
        label = "Suspicious"
        ip = random.choice(suspicious_ips)

    data.append({
        "login_hour": login_hour,
        "eventName": random.choice(all_events),
        "region": random.choice(regions),
        "userType": user_type,
        "sourceIP": ip,
        "cloudProvider": random.choice(clouds),
        "label": label
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Shuffle dataset
df = df.sample(frac=1).reset_index(drop=True)

# Save dataset
df.to_csv("multi_cloud_dataset_10000.csv", index=False)

# Display info
print(" Dataset Generated Successfully!\n")

print(" Sample Data:")
print(df.head())

print("\n Class Distribution:")
print(df["label"].value_counts())