import pandas as pd
import numpy as np

def generate_fan_chart_data(df, cycle_data):
    """
    Generates data for a Fan Chart prediction based on previous cycle performance.
    
    This function analyzes the growth patterns (multipliers relative to start price) of previous
    Bitcoin cycles (specifically Cycle 2 and 3) and projects them onto the current cycle (Cycle 4).
    It calculates a median path as well as minimum and maximum range boundaries.
    
    Args:
        df (pd.DataFrame): Historical price dataframe.
        cycle_data (dict): Processed cycle data from cycles.py containing 'data', 'start_date', etc.
    
    Returns:
        pd.DataFrame: DataFrame indexed by future dates with columns:
                      - 'median_price': The projected median price path.
                      - 'min_price': The lower bound of the projection.
                      - 'max_price': The upper bound of the projection.
    """
    if df.empty:
        return pd.DataFrame()

    # Get current cycle start date (Cycle 4)
    current_cycle = cycle_data.get(4) # Cycle 4 started in 2024
    if not current_cycle:
        return pd.DataFrame()
        
    start_date = current_cycle['start_date']
    current_prices = current_cycle['data']
    
    if current_prices.empty:
        return pd.DataFrame()

    # Normalize current cycle prices (start at 1.0)
    # We use the actual start price of the current cycle as the baseline for projection scaling
    start_price = current_prices.iloc[0]['price']
    
    # Analyze previous cycles (2 and 3) to get growth multiples
    # Cycle 1 is often an outlier due to extreme volatility, so we focus on 2 and 3 for more realistic projections.
    
    multipliers = []
    max_days = 0
    
    for c_num in [2, 3]:
        c_data = cycle_data.get(c_num)
        if c_data:
            c_df = c_data['data']
            if not c_df.empty:
                # Normalize prices: Calculate multiple of the cycle's starting price
                c_start_price = c_df.iloc[0]['price']
                c_multipliers = c_df['price'] / c_start_price
                
                # We need to re-index by "days since halving" to align timelines
                c_days = (c_df.index - c_data['start_date']).days
                
                # Create a series indexed by days
                series = pd.Series(c_multipliers.values, index=c_days)
                multipliers.append(series)
                
                if c_days.max() > max_days:
                    max_days = c_days.max()

    # Create a DataFrame to hold all multipliers aligned by day
    # We project out to 1460 days (approx 4 years) to cover the full expected cycle
    projection_days = range(0, 1460) 
    
    proj_df = pd.DataFrame(index=projection_days)
    
    for i, s in enumerate(multipliers):
        # Reindex to fill missing days if any using forward fill (propagate last valid observation)
        s_reindexed = s.reindex(projection_days, method='ffill')
        proj_df[f'cycle_{i+2}'] = s_reindexed
        
    # Calculate stats for fan chart (Median, Min, Max) across the historical multipliers
    proj_df['median'] = proj_df.median(axis=1)
    proj_df['min'] = proj_df.min(axis=1)
    proj_df['max'] = proj_df.max(axis=1)
    
    # Scale back to absolute prices using the current cycle's start price
    result = pd.DataFrame()
    result['days_since_halving'] = proj_df.index
    result['median_price'] = proj_df['median'] * start_price
    result['min_price'] = proj_df['min'] * start_price
    result['max_price'] = proj_df['max'] * start_price
    
    # Add actual calendar dates to the projection
    result['date'] = [start_date + pd.Timedelta(days=d) for d in result['days_since_halving']]
    
    return result.set_index('date')
