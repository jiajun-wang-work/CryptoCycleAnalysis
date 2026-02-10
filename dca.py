import pandas as pd
import numpy as np

def calculate_dca(df, amount, frequency="Monthly", start_date=None, end_date=None):
    """
    Calculates the performance of a Dollar Cost Averaging (DCA) strategy.
    
    Args:
        df (pd.DataFrame): DataFrame with 'price' column and datetime index.
        amount (float): Amount to invest per period in USD.
        frequency (str): Investment frequency - 'Daily', 'Weekly', or 'Monthly'.
        start_date (datetime, optional): Start date for the backtest.
        end_date (datetime, optional): End date for the backtest.
        
    Returns:
        dict: A dictionary containing:
              - 'history': DataFrame of portfolio value over time.
              - 'total_invested': Total USD amount invested.
              - 'final_value': Final USD value of the portfolio.
              - 'total_btc': Total amount of crypto asset accumulated.
              - 'roi': Return on Investment percentage.
              - 'max_drawdown': Maximum percentage drop from peak value.
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

    # Resample based on frequency to determine investment dates
    if frequency == "Monthly":
        # First day of the month
        investment_dates = df.resample('MS').first()
    elif frequency == "Weekly":
        # Every Monday
        investment_dates = df.resample('W-MON').first()
    else: # Daily
        investment_dates = df

    # Drop NaNs (skip days/weeks without price data)
    investment_dates = investment_dates.dropna()

    # Calculate portfolio accumulation
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
    # 1. Calculate the rolling peak value up to each point
    results_df['peak_value'] = results_df['value'].cummax()
    # 2. Calculate the percentage drop from that peak
    results_df['drawdown'] = (results_df['value'] - results_df['peak_value']) / results_df['peak_value']
    # 3. Find the minimum (most negative) drawdown
    max_drawdown = results_df['drawdown'].min() * 100 # Percentage

    # Final statistics
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
