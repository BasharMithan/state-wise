import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

n = 2000

timestamps = pd.date_range(
    start="2024-01-01 00:00:00",
    periods=n,
    freq="1h",
    tz="UTC"
)

open_price = 100.0

returns = np.random.normal(loc=0.0002, scale=0.015, size=n)

close_prices = np.cumprod(1 + returns) * open_price

high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.008, n)))
low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.008, n)))

open_prices = np.roll(close_prices, 1)
open_prices[0] = open_price

volume = np.random.lognormal(mean=10, sigma=0.5, size=n)

taker_buy_volume = volume * (0.5 + np.random.normal(0, 0.15, n))
taker_buy_volume = np.clip(taker_buy_volume, 0.05 * volume, 0.95 * volume)

trades = np.random.poisson(lam=200, size=n).astype(int)

df = pd.DataFrame({
    "open_time": timestamps,
    "symbol": "FAKEUSDT",
    "interval": "1h",
    "open": open_prices,
    "high": high_prices,
    "low": low_prices,
    "close": close_prices,
    "volume": volume,
    "trades": trades,
    "taker_buy_volume": taker_buy_volume
})

df["taker_buy_quote_volume"] = df["taker_buy_volume"] * df["close"]

out = Path("output/fake_stock_data.csv")
out.parent.mkdir(exist_ok=True)
df.to_csv(out, index=False)
out.stat().st_size