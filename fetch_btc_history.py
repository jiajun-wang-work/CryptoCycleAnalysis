import requests
import pandas as pd
import datetime
import time

def fetch_btc_full_history():
    """
    Fetches BTC full history from CryptoCompare (which has data back to 2010)
    and saves to CSV.
    """
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    
    # We want data up to now
    to_ts = int(time.time())
    all_data = []
    
    limit = 2000 # Max limit per request
    
    print("Fetching BTC history...")
    
    while True:
        params = {
            "fsym": "BTC",
            "tsym": "USD",
            "limit": limit,
            "toTs": to_ts
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["Response"] != "Success":
            print("Error:", data.get("Message"))
            break
            
        hourly_data = data["Data"]["Data"]
        if not hourly_data:
            break
            
        # Prepend data (since we are going backwards in time? No, toTs is end time)
        # CryptoCompare returns data ENDING at toTs.
        # So we get the last 2000 days.
        # Then we need to update toTs to be the start of this batch - 1
        
        # Actually, let's look at the data. 
        # It returns chronological list.
        # The first item is the oldest in this batch.
        
        # We collect this batch
        all_data = hourly_data + all_data
        
        first_ts = hourly_data[0]["time"]
        to_ts = first_ts - 1
        
        print(f"Fetched batch ending {datetime.datetime.fromtimestamp(hourly_data[-1]['time'])}. Oldest in batch: {datetime.datetime.fromtimestamp(first_ts)}")
        
        # Check if we have reached the beginning (Genesis is 2009, so ts > 0)
        # Or if no more data is returned
        if first_ts < 1230940800: # 2009-01-03
            break
            
        # Safety break
        if len(all_data) > 6000: # ~16 years
            break
            
        time.sleep(0.5)

    if not all_data:
        print("No data fetched.")
        return

    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Clean up
    df["timestamp"] = pd.to_datetime(df["time"], unit="s")
    df["price"] = df["close"]
    df = df[["timestamp", "price"]]
    
    # Remove duplicates
    df.drop_duplicates(subset="timestamp", inplace=True)
    df.sort_values("timestamp", inplace=True)
    
    # Filter valid prices
    df = df[df["price"] > 0]
    
    output_file = "btc_daily_data.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} records to {output_file}")
    
    # Verify
    print(df.head())
    print(df.tail())

if __name__ == "__main__":
    fetch_btc_full_history()
