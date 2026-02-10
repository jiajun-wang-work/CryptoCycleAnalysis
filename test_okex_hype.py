from utils import fetch_current_price, fetch_coin_history, COINS

def test_hype_price():
    coin_name = "Hyperliquid (HYPE)"
    print(f"Testing fetch for {coin_name}...")
    
    # Test current price
    price_data = fetch_current_price(coin_name)
    if price_data:
        print(f"Current Price: {price_data}")
    else:
        print("Failed to fetch current price.")

    # Test history
    df, source = fetch_coin_history(coin_name)
    if not df.empty:
        print(f"History fetched successfully from {source}. Rows: {len(df)}")
        print(df.tail())
    else:
        print("Failed to fetch history.")

if __name__ == "__main__":
    test_hype_price()
