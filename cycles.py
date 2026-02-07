import pandas as pd
import datetime

# Halving Dates (Cycle 0 is Genesis)
HALVING_DATES = {
    0: "2009-01-03", # Genesis Block
    1: "2012-11-28",
    2: "2016-07-09",
    3: "2020-05-11",
    4: "2024-04-20"
}

def get_cycle_data(df):
    """
    Segments the DataFrame into cycles based on halving dates.
    """
    cycles = {}
    
    # Sort dates to ensure order
    sorted_dates = sorted(HALVING_DATES.items())
    
    for i in range(len(sorted_dates)):
        cycle_num, start_date_str = sorted_dates[i]
        start_date = pd.to_datetime(start_date_str)
        
        # Determine end date (next halving date or today)
        if i < len(sorted_dates) - 1:
            end_date = pd.to_datetime(sorted_dates[i+1][1])
        else:
            end_date = pd.Timestamp.now()
            
        # Filter data
        cycle_df = df[(df.index >= start_date) & (df.index < end_date)].copy()
        
        # Calculate "Days Since Halving"
        cycle_df["days_since_halving"] = (cycle_df.index - start_date).days
        
        # Normalize price (optional: price / price_at_halving)
        if not cycle_df.empty:
            start_price = cycle_df.iloc[0]["price"]
            cycle_df["price_normalized"] = cycle_df["price"] / start_price
            
            # Find Highs and Lows
            high_price = cycle_df["price"].max()
            low_price = cycle_df["price"].min()
            high_date = cycle_df["price"].idxmax()
            low_date = cycle_df["price"].idxmin()
            
            # Determine actual start date for this coin in this cycle
            actual_start_date = cycle_df.index.min()
            
            cycles[cycle_num] = {
                "data": cycle_df,
                "start_date": start_date, # BTC Halving Date (Theoretical)
                "actual_start_date": actual_start_date, # Coin's First Data Date in this cycle
                "end_date": end_date,
                "high": high_price,
                "high_date": high_date,
                "high_days": (high_date - start_date).days,
                "low": low_price,
                "low_date": low_date,
                "current_days": (pd.Timestamp.now() - start_date).days if i == len(sorted_dates) - 1 else None
            }
            
    return cycles

def get_current_cycle_progress():
    last_halving = pd.to_datetime(HALVING_DATES[4])
    now = pd.Timestamp.now()
    days_passed = (now - last_halving).days
    
    # Estimate cycle length (approx 4 years = 1460 days)
    total_days = 1460
    progress = min(days_passed / total_days, 1.0)
    
    return {
        "days_passed": days_passed,
        "progress_pct": progress * 100,
        "halving_date": last_halving
    }
