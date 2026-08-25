from datetime import datetime


class HistoricalDataLoader:
    """Loads historical data from Binance"""
    
    def __init__(self, start: datetime, end: datetime) -> None:
        ...


    def load(self) -> dict:
        ...