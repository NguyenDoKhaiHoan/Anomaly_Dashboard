from __future__ import annotations

import math
import random
from pathlib import Path
from app.services.stream.sources.csv_source import CSVRowSource

# Columns to exclude from IoT CSV (not sensor data)
EXCLUDED_COLUMNS = {"Device_ID", "Anomaly", "Timestamp", "index", "Index"}

class IoTSensorStream:
    def __init__(self, dataset_path: str | None = None):
        self.source = None
        self.step = 0
        if dataset_path:
            path = Path(dataset_path)
            try:
                self.source = CSVRowSource(path)
            except FileNotFoundError:
                self.source = None

    def next_event(self) -> dict:
        self.step += 1
        if self.source and self.source.has_data():
            row = self.source.next_row()
            # Filter out non-sensor columns and convert to float
            event = {}
            for k, v in row.items():
                if k not in EXCLUDED_COLUMNS:
                    # Convert numeric values to float
                    try:
                        event[k] = float(v) if str(v).replace(".", "", 1).replace("-", "", 1).replace("e", "", 1).isdigit() else v
                    except (ValueError, AttributeError):
                        event[k] = v
            return event
        
        # Fallback to synthetic data if CSV not available
        baseline_temp = 28 + math.sin(self.step / 8) * 2
        baseline_hum = 60 + math.cos(self.step / 10) * 5
        battery = max(10, 100 - self.step * 0.08 + random.uniform(-0.5, 0.5))
        if self.step % 47 == 0:
            baseline_temp += random.uniform(7, 12)
            baseline_hum += random.uniform(10, 18)
        return {
            "Temperature": round(baseline_temp + random.uniform(-0.3, 0.3), 3),
            "Humidity": round(baseline_hum + random.uniform(-1.0, 1.0), 3),
            "Battery_Level": round(battery, 3),
        }
