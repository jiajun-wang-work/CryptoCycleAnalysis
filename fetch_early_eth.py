import requests
import pandas as pd
from datetime import datetime
import time
import os

def fetch_eth_early():
    print("Attempting to fetch ETH early history (2015-2017)...")
    
    # Target: From Launch (Aug 2015) to End of 2017
    # 2017-12-31 = 1514764800
    to_ts = 1514764800
    limit = 2000 # Should cover 2015-2017 (approx 900 days)
    
    # 1. Try CryptoCompare (Usually very reliable for history)
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        "fsym": "ETH",
        "tsym": "USD",
        "limit": limit,
        "toTs": to_ts
    }
    
    try:
        print("1. Requesting CryptoCompare...")
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        if data.get("Response") == "Success":
            days = data["Data"]["Data"]
            print(f"   Received {len(days)} records.")
            
            # Extract time and close price
            records = []
            for d in days:
                ts = d["time"]
                price = d["close"]
                records.append({"timestamp": datetime.fromtimestamp(ts), "price": price})
            
            df = pd.DataFrame(records)
            df.set_index("timestamp", inplace=True)
            
            # Filter for meaningful price (ETH started around $0.3 - $3.0)
            # Remove 0s if any
            df = df[df["price"] > 0]
            
            print(f"   Date Range: {df.index.min()} to {df.index.max()}")
            
            # Save to CSV
            filename = "eth_early_2015_2017.csv"
            df.to_csv(filename)
            print(f"   Saved to {filename}")
            return True
        else:
            print(f"   Failed: {data.get('Message')}")
            
    except Exception as e:
        print(f"   Error: {e}")

    return False

if __name__ == "__main__":
    fetch_eth_early()
