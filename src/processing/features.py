import pandas as pd
import numpy as np

def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily log-returns."""
    df['Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    return df

def compute_ema(df: pd.DataFrame, span: int = 20) -> pd.DataFrame:
    """Compute Exponential Moving Average."""
    df[f'EMA_{span}'] = df['Close'].ewm(span=span, adjust=False).mean()
    return df

def compute_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Compute Relative Strength Index."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    df[f'RSI_{window}'] = 100 - (100 / (1 + rs))
    return df

def compute_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Compute rolling volatility."""
    if 'Returns' not in df.columns:
        df = compute_returns(df)
    df['Volatility'] = df['Returns'].rolling(window=window).std() * np.sqrt(252) # Annualized
    return df

def get_rolling_mean(df: pd.DataFrame, column: str, window: int) -> pd.Series:
    """
    Apply C++ rolling mean if available, else fallback to pandas.
    """
    try:
        import cpp_features
        return pd.Series(cpp_features.rolling_mean(df[column].values, window), index=df.index)
    except (ImportError, ModuleNotFoundError):
        # Log once to inform user of fallback
        if not hasattr(get_rolling_mean, "_logged"):
            from loguru import logger
            logger.info("C++ optimization module not found. Using optimized Python/Pandas fallback.")
            get_rolling_mean._logged = True
        return df[column].rolling(window=window).mean()

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate indicator set per ticker.
    """
    # Defensive sort
    df = df.sort_values(['Symbol', 'Date'])
    
    def process_group(group):
        group = compute_returns(group)
        group = compute_ema(group, 20)
        group = compute_rsi(group, 14)
        group = compute_volatility(group, 20)
        group['SMA_20_Fallback'] = get_rolling_mean(group, 'Close', 20)
        return group

    return df.groupby('Symbol', group_keys=False).apply(process_group).sort_values('Date')
