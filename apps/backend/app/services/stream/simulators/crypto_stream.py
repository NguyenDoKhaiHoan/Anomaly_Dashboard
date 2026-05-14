from __future__ import annotations
import random

class CryptoMarketStream:
    def __init__(self, symbol: str = "BTC"):
        self.symbol = symbol.upper()
        self.price = {"BTC": 62000.0, "ETH": 3000.0, "SOL": 140.0}.get(self.symbol, 100.0)
        self.step = 0

    def next_event(self) -> dict:
        self.step += 1
        drift = random.uniform(-0.007, 0.007)
        shock = random.uniform(0.03, 0.08) if self.step % 53 == 0 else 0.0
        direction = random.choice([-1, 1]) if shock else 1
        self.price *= (1 + drift + direction * shock)
        volume = max(1000.0, abs(random.gauss(20000, 5000)))
        return {"symbol": self.symbol, "price": round(self.price, 2), "volume": round(volume, 2)}
