import requests
import pandas as pd


def fetch_bitcoin_data():

    url = "https://api.binance.com/api/v3/klines"
    params ={
        "symbol": "BTCUSDT",
        "interval": "1d",
        "limit": 200
    }

    response = requests.get(url,params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume",
                                      "close_time", "quote_asset_volume", "trades",
                                        "taker_base_volume", "taker_quote_volume", "ignore"])
    df["close"] = df["close"].astype(float)
    return df


def calculate_indicators():
    df = fetch_bitcoin_data()

    df["SMA50"] = df["close"].rolling(window=50).mean()
    df["SMA200"] = df["close"].rolling(window=200).mean()

    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()     
    rs = gain / loss
    df["RSI"] = 100 - (100/ (1 + rs))

    df["EMA12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]

    latest = df.iloc[-1]

    trends = {
        "SMA50": "صعودی" if latest["close"] > latest["SMA50"] else "نزولی",
        "SMA200": "صعودی" if latest["close"] > latest["SMA200"] else "نزولی",
        "RSI": "صعودی" if latest["RSI"] > 50 else "نزولی",
        "MACD": "صعودی" if latest["MACD"] > 0 else "نزولی",

    }

    return trends

