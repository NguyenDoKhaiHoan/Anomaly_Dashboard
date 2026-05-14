import json
import pickle
from pathlib import Path

# Load metadata.json
metadata_path = Path(r"C:\Users\Dell\Desktop\Anomaly_Dashboard\Project2\models\fraud\metadata.json")
output_path = Path(r"C:\Users\Dell\Desktop\Anomaly_Dashboard\Project2\models\fraud\statistical_fraud_model.pkl")

with open(metadata_path, "r", encoding="utf-8") as f:
    bundle = json.load(f)

print(f"Loaded threshold: {bundle.get('threshold')}")

with open(output_path, "wb") as f:
    pickle.dump(bundle, f)

print(f"Updated: {output_path}")
