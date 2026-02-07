import pandas as pd
import numpy as np

def calculate_dca(df, amount, frequency="Monthly", start_date=None, end_date=None):
    """
    Calculates DCA performance.
    
    Args:
        df: DataFrame with 'price' column and datetime index.
        amount: Amount to invest per period.
        frequency: 'Daily', 'Weekly', 'Monthly'.
        start_date: Start date for backtest.
        end_date: End date for backtest.
    """
    if df.empty:
        return None

    # Filter by date range
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]
        
    if df.empty:
        return None

    # Resample based on frequency
    if frequency == "Monthly":
        # First day of the month
        investment_dates = df.resample('MS').first()
    elif frequency == "Weekly":
        investment_dates = df.resample('W-MON').first()
    else: # Daily
        investment_dates = df

    # Drop NaNs (days without price data)
    investment_dates = investment_dates.dropna()

    # Calculate portfolio
    total_invested = 0
    total_btc = 0
    history = []

    for date, row in investment_dates.iterrows():
        price = row['price']
        btc_bought = amount / price
        total_invested += amount
        total_btc += btc_bought
        
        current_value = total_btc * price
        roi = (current_value - total_invested) / total_invested * 100
        
        history.append({
            "date": date,
            "invested": total_invested,
            "value": current_value,
            "btc_accumulated": total_btc,
            "roi": roi,
            "price": price
        })
        
    results_df = pd.DataFrame(history).set_index("date")
    
    # Calculate Max Drawdown of the Portfolio Value
    # Calculate rolling max
    results_df['peak_value'] = results_df['value'].cummax()
    results_df['drawdown'] = (results_df['value'] - results_df['peak_value']) / results_df['peak_value']
    max_drawdown = results_df['drawdown'].min() * 100 # Percentage

    # Final stats
    final_value = results_df.iloc[-1]['value']
    final_invested = results_df.iloc[-1]['invested']
    final_roi = results_df.iloc[-1]['roi']
    
    return {
        "history": results_df,
        "total_invested": final_invested,
        "final_value": final_value,
        "total_btc": total_btc,
        "roi": final_roi,
        "max_drawdown": max_drawdown
    }

def smart_dca_strategy(df, base_amount, ma_period=200):
    """
    Example Smart DCA: Buy more when price < MA200.
    """
    # Calculate MA
    df['ma'] = df['price'].rolling(window=ma_period).mean()
    
    # ... logic implementation ...
    # For MVP, we stick to standard DCA first as per PRD "Scenario 1" mostly focuses on simple output first, 
    # though "Smart DCA" is mentioned. I'll stick to standard DCA for the basic function first.
    pass
