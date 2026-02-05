import pandas as pd
from .base_strategy import BaseStrategy

class MovingAverageCross(BaseStrategy):
    """
    Simple Moving Average Crossover strategy.
    Long when fast EMA > slow EMA, short otherwise.
    """
    
    def __init__(self, fast_window: int = 10, slow_window: int = 30):
        super().__init__({"fast_window": fast_window, "slow_window": slow_window})
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Sort by ticker and time
        df = df.sort_values(['Symbol', 'Date']).copy()
        
        def process_group(group):
            # Calculate EMAs for crossover signals
            group['EMA_Fast'] = group['Close'].ewm(span=self.fast_window, adjust=False).mean()
            group['EMA_Slow'] = group['Close'].ewm(span=self.slow_window, adjust=False).mean()
            return group

        df = df.groupby('Symbol', group_keys=False).apply(process_group)
        
        def calculate_weights(daily_group):
            # All symbols start with zero allocation
            daily_group['Target_Position'] = 0.0
            
            # Trend following: entry when fast EMA > slow EMA
            daily_group['Signal'] = 0
            daily_group.loc[daily_group['EMA_Fast'] > daily_group['EMA_Slow'], 'Signal'] = 1
            
            # Count active signals
            active_mask = daily_group['Signal'] == 1
            num_active = active_mask.sum()
            
            if num_active > 0:
                # Risk Parity: Scale positions inversely to volatility
                vol = daily_group.loc[active_mask, 'Volatility'].fillna(daily_group['Volatility'].mean()).clip(lower=0.0001)
                inv_vol = 1.0 / vol
                weights = inv_vol / inv_vol.sum()
                
                # Normalize exposure. Using 0.95 to account for execution buffer.
                total_exposure = 0.95
                daily_group.loc[active_mask, 'Target_Position'] = weights * total_exposure
                
            return daily_group

        return df.groupby('Date', group_keys=False).apply(calculate_weights).sort_values('Date')
