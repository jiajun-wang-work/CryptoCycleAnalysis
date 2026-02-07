import requests
from utils import COINS

def test_eth_price():
    coin_name = "Ethereum (ETH)"
    cg_id, yahoo_ticker, binance_symbol = COINS[coin_name]
    
    print(f"Testing price fetch for {coin_name}...")
    print(f"IDs: CoinGecko={cg_id}, Yahoo={yahoo_ticker}, Binance={binance_symbol}")
    
    # 1. Test Binance
    print("\n--- Testing Binance ---")
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": binance_symbol}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Price: ${float(data['lastPrice']):,.2f}")
        else:
            print(f"Failed. Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Yahoo (via yfinance)
    print("\n--- Testing Yahoo Finance ---")
    try:
        import yfinance as yf
        ticker = yf.Ticker(yahoo_ticker)
        info = ticker.fast_info
        if info and info.last_price:
            print(f"Success! Price: ${info.last_price:,.2f}")
        else:
            print("Failed. No price data found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_eth_price()
