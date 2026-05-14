from __future__ import annotations
from pydantic import BaseModel

class FraudTransactionFeatures(BaseModel):
    amt: float
    city_pop: float
    card_holder_age: float
    trans_hour: int
    trans_weekday: int
    trans_month: int
    distance: float
    merchant: int
    category: int
    gender: int
    state: int
    job: int
