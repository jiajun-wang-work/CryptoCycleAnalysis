import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
import time

def check_eth_sources():
    print("=== Diagnosing ETH Data Sources ===")
    
    # 1. Yahoo Finance
    print("\n1. Checking Yahoo Finance (ETH-USD)...")
    try:
        eth_yahoo = yf.Ticker("ETH-USD").history(period="max")
        if not eth_yahoo.empty:
            print(f"   Start Date: {eth_yahoo.index[0]}")
            print(f"   End Date: {eth_yahoo.index[-1]}")
        else:
            print("   No data found.")
    except Exception as e:
        print(f"   Error: {e}")

    # 2. Binance
    print("\n2. Checking Binance (ETHUSDT)...")
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "ETHUSDT", "interval": "1d", "startTime": 0, "limit": 1}
        r = requests.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            if data:
                start_ts = data[0][0]
                start_date = datetime.fromtimestamp(start_ts/1000)
                print(f"   Start Date: {start_date}")
            else:
                print("   No data returned.")
        else:
            print(f"   Error: Status {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. CoinGecko (Try to fetch early data specifically)
    print("\n3. Checking CoinGecko (ethereum)...")
    try:
        # Try to get data from 2015-08-01 to 2015-08-05 to see if it works
        start_ts = int(datetime(2015, 8, 7).timestamp())
        end_ts = int(datetime(2015, 8, 10).timestamp())
        
        url = f"https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": start_ts,
            "to": end_ts
        }
        
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            prices = data.get("prices", [])
            if prices:
                print(f"   Success! Found {len(prices)} data points in 2015.")
                print(f"   First Point: {datetime.fromtimestamp(prices[0][0]/1000)} - ${prices[0][1]}")
            else:
                print("   No prices returned for 2015.")
        else:
            print(f"   Failed. Status: {r.status_code} (Likely Rate Limited)")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    check_eth_sources()
