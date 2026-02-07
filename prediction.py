import pandas as pd
import numpy as np

def generate_fan_chart_data(df, cycle_data):
    """
    Generates data for a Fan Chart prediction based on previous cycle performance.
    
    Args:
        df: Historical price dataframe
        cycle_data: Processed cycle data from cycles.py
    
    Returns:
        DataFrame with projected high, low, and median paths.
    """
    if df.empty:
        return pd.DataFrame()

    # Get current cycle start date
    current_cycle = cycle_data.get(4) # Cycle 4 started in 2024
    if not current_cycle:
        return pd.DataFrame()
        
    start_date = current_cycle['start_date']
    current_prices = current_cycle['data']
    
    if current_prices.empty:
        return pd.DataFrame()

    # Normalize current cycle prices (start at 1.0)
    start_price = current_prices.iloc[0]['price']
    
    # Analyze previous cycles (2 and 3) to get growth multiples
    # Cycle 1 is often an outlier due to extreme volatility, so we focus on 2 and 3
    # or we can use all available previous cycles.
    
    multipliers = []
    max_days = 0
    
    for c_num in [2, 3]:
        c_data = cycle_data.get(c_num)
        if c_data:
            c_df = c_data['data']
            if not c_df.empty:
                # Normalize prices
                c_start_price = c_df.iloc[0]['price']
                c_multipliers = c_df['price'] / c_start_price
                
                # We need to re-index by "days since halving"
                c_days = (c_df.index - c_data['start_date']).days
                
                # Create a series indexed by days
                series = pd.Series(c_multipliers.values, index=c_days)
                multipliers.append(series)
                
                if c_days.max() > max_days:
                    max_days = c_days.max()

    # Create a DataFrame to hold all multipliers aligned by day
    # We project out to 1000 days or max of previous cycles
    projection_days = range(0, 1460) # 4 years
    
    proj_df = pd.DataFrame(index=projection_days)
    
    for i, s in enumerate(multipliers):
        # Reindex to fill missing days if any
        s_reindexed = s.reindex(projection_days, method='ffill')
        proj_df[f'cycle_{i+2}'] = s_reindexed
        
    # Calculate stats for fan chart
    # We want to project from "Now" onwards
    # But for the visual, we usually show the whole cycle projection
    
    proj_df['median'] = proj_df.median(axis=1)
    proj_df['min'] = proj_df.min(axis=1)
    proj_df['max'] = proj_df.max(axis=1)
    
    # Scale back to current price
    # We use the Start Price of CURRENT cycle to project absolute values
    
    result = pd.DataFrame()
    result['days_since_halving'] = proj_df.index
    result['median_price'] = proj_df['median'] * start_price
    result['min_price'] = proj_df['min'] * start_price
    result['max_price'] = proj_df['max'] * start_price
    
    # Add actual dates
    result['date'] = [start_date + pd.Timedelta(days=d) for d in result['days_since_halving']]
    
    return result.set_index('date')
