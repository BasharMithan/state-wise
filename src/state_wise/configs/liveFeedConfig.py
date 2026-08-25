from dataclasses import dataclass


@dataclass
class LiveFeedConfig:
    symbol: list[str]
    interval: str = "1m"
    testnet: bool = True
    reconnectBackoffSeconds: float = 2.0
    maxBackoffSeconds: float = 60.0

    @property
    def webSocketBaseURL(self) -> str:
        return (
            "wss://stream.testnet.binance.vision/stream"
            if self.testnet
            else "wss://stream.binance.com:443/stream"
        )

    @property
    def streams(self) -> list[str]:
        return [
            f"{s.lower()}@kline_{self.interval}"
            for s in self.symbol
        ]