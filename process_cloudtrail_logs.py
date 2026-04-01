import json
import pandas as pd
import os

#  Folder where ALL your JSON files are stored
log_folder = r"D:\Cloud Security Project Implementation"

all_rows = []

print("Scanning folder for JSON files...\n")

for filename in os.listdir(log_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(log_folder, filename)
        print(f"Processing file: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Handle S3 format ({"Records": [...]})
                if isinstance(data, dict) and "Records" in data:
                    records = data["Records"]

                # Handle Event History format ([ {...}, {...} ])
                elif isinstance(data, list):
                    records = data

                else:
                    continue

                for record in records:
                    row = {
                        "eventTime": record.get("eventTime"),
                        "eventName": record.get("eventName"),
                        "eventSource": record.get("eventSource"),
                        "userType": record.get("userIdentity", {}).get("type"),
                        "userName": record.get("userIdentity", {}).get("userName"),
                        "sourceIP": record.get("sourceIPAddress"),
                        "mfaUsed": record.get("additionalEventData", {}).get("MFAUsed"),
                        "region": record.get("awsRegion"),
                        "eventID": record.get("eventID"),
                        "eventType": record.get("eventType")
                    }

                    all_rows.append(row)

        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Convert to DataFrame
df = pd.DataFrame(all_rows)

# Remove duplicates
df = df.drop_duplicates(subset=["eventID"])

# Convert time column
df["eventTime"] = pd.to_datetime(df["eventTime"], errors="coerce")

# Sort by time
df = df.sort_values("eventTime")

# Save dataset
df.to_csv("cloudtrail_dataset.csv", index=False)

print("\n Dataset Updated Successfully!")
print("Total Unique Records:", len(df))

print("\n Event Distribution:")
print(df["eventName"].value_counts())

print("\n ConsoleLogin Events:")
print(df[df["eventName"] == "ConsoleLogin"])