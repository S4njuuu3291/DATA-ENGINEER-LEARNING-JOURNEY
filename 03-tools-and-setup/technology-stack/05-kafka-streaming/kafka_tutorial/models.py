import time
from typing import Optional

from pydantic import BaseModel


class TradeEvent(BaseModel):
    symbol: str
    price: float
    event_time: int
    processed_at: int

    @classmethod
    def from_binance(cls, raw: dict):
        return cls(
            symbol=raw["s"],
            price=float(raw["p"]),
            # price="INVALID",
            event_time=raw["T"] // 1000,
            processed_at=int(time.time()),
        )
