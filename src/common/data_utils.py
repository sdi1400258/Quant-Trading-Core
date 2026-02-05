import pandas as pd
import numpy as np
from loguru import logger

def validate_ohlcv(df: pd.DataFrame) -> bool:
    """
    Check OHLCV data for consistency and missing values.
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        return False
        
    # Check for NaN values
    if df[required_columns].isnull().any().any():
        logger.warning(f"Found NaN values in OHLCV data. Rows: {df[df[required_columns].isnull().any(axis=1)]}")
        # Optionally drop or fill NaNs. For now, just log.
        
    # Logical checks
    mask = (df['High'] < df['Low']) | (df['High'] < df['Open']) | (df['High'] < df['Close']) | \
           (df['Low'] > df['Open']) | (df['Low'] > df['Close'])
    
    if mask.any():
        logger.error(f"Inconsistent price levels detected at: {df[mask].index}")
        return False
        
    return True

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures consistent column casing.
    """
    df.columns = [col.capitalize() for col in df.columns]
    return df

def adjust_for_splits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Placeholder for corporate action adjustment logic.
    Note: yf.download(auto_adjust=True) handles most of this.
    """
    return df
