from __future__ import annotations
from pydantic import BaseModel

class IoTReadingFeatures(BaseModel):
    Temperature: float
    Humidity: float
    Battery_Level: float
    temp_diff: float
    hum_diff: float
    bat_diff: float
    temp_mean10: float
    temp_std10: float
    hum_mean10: float
    hum_std10: float
