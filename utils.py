import requests
import pandas as pd
import streamlit as st
import yfinance as yf
import time
import os
from datetime import datetime

# CoinGecko API URL
BASE_URL = "https://api.coingecko.com/api/v3"

# Top 20 Coins Mapping
# Name: (CoinGecko ID, Yahoo Ticker, Binance Symbol)
COINS = {
    "Bitcoin (BTC)": ("bitcoin", "BTC-USD", "BTCUSDT"),
    "Ethereum (ETH)": ("ethereum", "ETH-USD", "ETHUSDT"),
    "Binance Coin (BNB)": ("binancecoin", "BNB-USD", "BNBUSDT"),
    "Solana (SOL)": ("solana", "SOL-USD", "SOLUSDT"),
    "XRP (XRP)": ("ripple", "XRP-USD", "XRPUSDT"),
    "Cardano (ADA)": ("cardano", "ADA-USD", "ADAUSDT"),
    "Dogecoin (DOGE)": ("dogecoin", "DOGE-USD", "DOGEUSDT"),
    "Avalanche (AVAX)": ("avalanche-2", "AVAX-USD", "AVAXUSDT"),
    "TRON (TRX)": ("tron", "TRX-USD", "TRXUSDT"),
    "Polkadot (DOT)": ("polkadot", "DOT-USD", "DOTUSDT"),
    "Chainlink (LINK)": ("chainlink", "LINK-USD", "LINKUSDT"),
    "Polygon (MATIC)": ("matic-network", "MATIC-USD", "MATICUSDT"),
    "Toncoin (TON)": ("the-open-network", "TON11419-USD", "TONUSDT"),
    "Shiba Inu (SHIB)": ("shiba-inu", "SHIB-USD", "SHIBUSDT"),
    "Litecoin (LTC)": ("litecoin", "LTC-USD", "LTCUSDT"),
    "Bitcoin Cash (BCH)": ("bitcoin-cash", "BCH-USD", "BCHUSDT"),
    "Ethereum Classic (ETC)": ("ethereum-classic", "ETC-USD", "ETCUSDT"),
    "Stellar (XLM)": ("stellar", "XLM-USD", "XLMUSDT"),
    "Monero (XMR)": ("monero", "XMR-USD", "XMRUSDT"),
    "Cosmos (ATOM)": ("cosmos", "ATOM-USD", "ATOMUSDT")
}

def fetch_coin_history_yahoo(ticker_symbol):
    """
    Fetches historical data from Yahoo Finance as a fallback.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch max history
        hist = ticker.history(period="max")
        
        if hist.empty:
            return pd.DataFrame()
            
        # Standardize columns to match our app's expectation
        # We need index as datetime and a 'price' column
        df = pd.DataFrame()
        df["price"] = hist["Close"]
        
        # Ensure index is timezone-naive or matches app logic
        df.index = df.index.tz_localize(None)
        
        return df
    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol} from Yahoo Finance: {e}")
        return pd.DataFrame()

def fetch_coin_history_binance(symbol):
    """
    Fetches historical data from Binance API (No Key Required).
    Iterates to fetch full history.
    """
    base_url = "https://api.binance.com/api/v3/klines"
    all_data = []
    
    # Start time (2017-01-01) - Binance launched around mid-2017
    start_ts = int(datetime(2017, 1, 1).timestamp() * 1000)
    end_ts = int(time.time() * 1000)
    
    # Limit per request is 1000. 1d interval.
    # We fetch in chunks
    current_start = start_ts
    
    try:
        while True:
            params = {
                "symbol": symbol,
                "interval": "1d",
                "startTime": current_start,
                "limit": 1000
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            if not data:
                break
                
            all_data.extend(data)
            
            # Last timestamp
            last_close_time = data[-1][6]
            current_start = last_close_time + 1
            
            if current_start >= end_ts:
                break
                
            # Rate limit protection
            time.sleep(0.1)
            
        if not all_data:
            return pd.DataFrame()

        # Parse data
        # Binance kline: [open_time, open, high, low, close, vol, close_time...]
        df = pd.DataFrame(all_data, columns=[
            "open_time", "open", "high", "low", "close", "volume", 
            "close_time", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
        df["price"] = df["close"].astype(float)
        df.set_index("timestamp", inplace=True)
        
        return df[["price"]]
        
    except Exception as e:
        # Binance might not have the symbol or other error
        # st.warning(f"Binance API error for {symbol}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_coin_history(coin_name, api_key=None, source="Auto"):
    """
    Fetches the entire price history of a coin.
    Source can be: "Auto", "CoinGecko", "Binance", "Yahoo"
    """
    cg_id, yahoo_ticker, binance_symbol = COINS.get(coin_name, ("bitcoin", "BTC-USD", "BTCUSDT"))
    
    # Logic for Source Selection
    
    # 1. Force CoinGecko
    if source == "CoinGecko" and api_key:
        return _fetch_coingecko(cg_id, api_key), "CoinGecko"
        
    # 2. Force Binance
    if source == "Binance":
        df = fetch_coin_history_binance(binance_symbol)
        if not df.empty: return df, "Binance"
        
    # 3. Force Yahoo
    if source == "Yahoo":
        return fetch_coin_history_yahoo(yahoo_ticker), "Yahoo Finance"
        
    # 4. Auto Mode (Default)
    # Priority: CoinGecko (Best Data) -> Combine(Yahoo + Binance)
    
    # Try CoinGecko first (even without key, for best history coverage)
    df_cg = _fetch_coingecko(cg_id, api_key)
    if not df_cg.empty: 
        return df_cg, "CoinGecko"
        
    # If CoinGecko fails, we try to combine Yahoo (longer history) and Binance (better quality recent)
    df_yahoo = fetch_coin_history_yahoo(yahoo_ticker)
    df_binance = fetch_coin_history_binance(binance_symbol)
    
    # SPECIAL HANDLING FOR ETH: Load local early history (2015-2017)
    df_local = pd.DataFrame()
    if cg_id == "ethereum":
        try:
            local_file = "eth_early_2015_2017.csv"
            if os.path.exists(local_file):
                df_local = pd.read_csv(local_file)
                df_local["timestamp"] = pd.to_datetime(df_local["timestamp"])
                df_local.set_index("timestamp", inplace=True)
                # Ensure index is timezone-naive
                df_local.index = df_local.index.tz_localize(None)
        except Exception as e:
            pass # Ignore if local file fails

    # Merge Logic
    # Priority: Local (Oldest) -> Yahoo (Middle) -> Binance (Newest)
    
    source_name = "Hybrid (Yahoo/Binance)"
    
    # Start with whatever we have locally
    current_df = df_local
    if not df_local.empty:
        source_name = "Hybrid (Local/Yahoo/Binance)"
    
    # Merge Yahoo
    if not df_yahoo.empty:
        if current_df.empty:
            current_df = df_yahoo
            source_name = "Yahoo Finance"
        else:
            # Append Yahoo data that is NEWER than local
            last_local = current_df.index.max()
            yahoo_new = df_yahoo[df_yahoo.index > last_local]
            current_df = pd.concat([current_df, yahoo_new])
            if not df_local.empty: source_name = "Hybrid (Local + Yahoo)"
            
    # Merge Binance
    if not df_binance.empty:
        if current_df.empty:
            current_df = df_binance
            source_name = "Binance"
        else:
            # Append Binance data that is NEWER than current
            # But wait, Binance is better than Yahoo for recent. 
            # So if we have overlapping Yahoo/Binance, we prefer Binance.
            
            binance_start = df_binance.index.min()
            
            # Keep current data strictly BEFORE Binance starts
            current_early = current_df[current_df.index < binance_start]
            
            # Combine
            current_df = pd.concat([current_early, df_binance])
            
            if not df_local.empty:
                source_name = "Hybrid (Local + Yahoo + Binance)"
            elif not df_yahoo.empty:
                source_name = "Hybrid (Yahoo + Binance)"
            
    if not current_df.empty:
        # Final cleanup
        current_df = current_df[~current_df.index.duplicated(keep='last')]
        current_df.sort_index(inplace=True)
        return current_df, source_name
        
    return pd.DataFrame(), "None"

def _fetch_coingecko(cg_id, api_key):
    url = f"{BASE_URL}/coins/{cg_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "max",
        "interval": "daily"
    }
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    
    try:
        # Short timeout to avoid hanging if rate limited
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            prices = data.get("prices", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_current_price(coin_name, api_key=None):
    """
    Fetches the current price of a coin.
    """
    cg_id, yahoo_ticker, binance_symbol = COINS.get(coin_name, ("bitcoin", "BTC-USD", "BTCUSDT"))

    # Try CoinGecko first
    # Even without key, we try it once (it might work and has best data)
    try:
        url = f"{BASE_URL}/simple/price"
        params = {
            "ids": cg_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        headers = {}
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        
        response = requests.get(url, params=params, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if cg_id in data:
                return data[cg_id]
    except:
        pass
    
    # Try Binance for current price
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": binance_symbol}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "usd": float(data["lastPrice"]),
                "usd_24h_change": float(data["priceChangePercent"])
            }
    except:
        pass
            
    # Fallback to Yahoo Finance
    try:
        ticker = yf.Ticker(yahoo_ticker)
        # Get fast info
        info = ticker.fast_info
        if info and info.last_price:
            # Yahoo doesn't give 24h change directly in fast_info easily without history
            # Let's get 2 days history to calc change
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                last = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = ((last - prev) / prev) * 100
                return {
                    "usd": last,
                    "usd_24h_change": change
                }
            else:
                return {
                    "usd": info.last_price,
                    "usd_24h_change": 0.0
                }
    except Exception as e:
        st.error(f"Error fetching current price for {coin_name}: {e}")
        return None
