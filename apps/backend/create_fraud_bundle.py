import json
import pickle
from pathlib import Path

# Load metadata.json
metadata_path = Path(__file__).parent.parent.parent.parent / "models" / "fraud" / "metadata.json"
with open(metadata_path, "r", encoding="utf-8") as f:
    bundle = json.load(f)

# Save as .pkl
output_path = Path(__file__).parent / "models" / "fraud" / "statistical_fraud_model.pkl"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "wb") as f:
    pickle.dump(bundle, f)

print(f"Created: {output_path}")
print(f"Content: {bundle}")
