import yfinance as yf
import pandas as pd

def test_btc_yahoo():
    ticker = "BTC-USD"
    print(f"Fetching history for {ticker} from Yahoo...")
    t = yf.Ticker(ticker)
    hist = t.history(period="max")
    
    if not hist.empty:
        print(f"Start Date: {hist.index[0]}")
        print(f"End Date: {hist.index[-1]}")
        print(f"Total Rows: {len(hist)}")
    else:
        print("No history found.")

if __name__ == "__main__":
    test_btc_yahoo()
