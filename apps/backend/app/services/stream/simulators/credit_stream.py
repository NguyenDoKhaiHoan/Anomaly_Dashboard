from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from app.services.stream.sources.csv_source import CSVRowSource

class CreditCardStream:
    def __init__(self, dataset_path: str | None = None):
        self.source = None
        if dataset_path:
            path = Path(dataset_path)
            try:
                self.source = CSVRowSource(path)
            except FileNotFoundError:
                self.source = None

    def next_event(self) -> dict:
        if self.source and self.source.has_data():
            return self.source.next_row()
        now = datetime.utcnow()
        base_lat = 10.8 + random.random()
        base_lon = 106.6 + random.random()
        birth_year = random.randint(1950, 2004)
        return {
            "trans_date_trans_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "merchant": random.choice(["amazon", "walmart", "ebay", "target"]),
            "category": random.choice(["shopping_net", "grocery_pos", "misc_net"]),
            "amt": round(random.uniform(5, 5000), 2),
            "gender": random.choice(["F", "M"]),
            "state": random.choice(["CA", "TX", "FL", "NC"]),
            "city_pop": random.randint(5000, 1_000_000),
            "job": random.choice(["Engineer", "Teacher", "Doctor", "Analyst"]),
            "dob": f"{birth_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "lat": round(base_lat, 6),
            "long": round(base_lon, 6),
            "merch_lat": round(base_lat + random.uniform(-0.8, 0.8), 6),
            "merch_long": round(base_lon + random.uniform(-0.8, 0.8), 6),
        }
