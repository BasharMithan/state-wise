from dataclasses import dataclass
from pydantic import BaseModel
from datetime import datetime


class Features(BaseModel):
    """Contains the necessary features for the HMM regime detector
    and the gradient boosting predictor that will be assigned to the candle.

    Features:
    1. `logReturn`:
    2. `mutiLogReturn`:
    3. bodyPercentage:
    4. rangePercentage:
    5. upperWick:
    6. lowerWick:
    7. closeLocation:
    """

    logReturn: float
    bodyPercentage: float
    rangePercentage: float
    bodyPercentage: float
    upperWick: float
    lowerWick: float
    closeLocation: float







@dataclass(frozen=True)
class Candle:
    """A single normalized OHLCV bar, identical whether it came from a
    live Binance stream or historical data."""

    symbol: list[str]
    timestamp: datetime     # bar CLOSE time — never the open time, to avoid
                            # any ambiguity about what data was actually
                            # available "at" this timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_final: bool           # False only for in-progress/unconfirmed bars;
                             # feature engineering must never consume these
                             # (see 02-feature-engineering.md's no-lookahead rule)

    source: str
    features: Features | None = None



    bid: str = ""
    ask: str = ""


    def __post_init__(self) -> None:
        # Cheap invariant checks — cheap enough to run on every bar, and
        # exactly the kind of thing that should fail loudly rather than
        # silently propagate a malformed observation downstream.

        if self.high < self.low:
            raise ValueError(f"{self.symbol}@{self.timestamp}: high < low")
        
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"{self.symbol}@{self.timestamp}: open outside [low, high]")
        
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"{self.symbol}@{self.timestamp}: close outside [low, high]")
        
        if self.volume < 0:
            raise ValueError(f"{self.symbol}@{self.timestamp}: negative volume")