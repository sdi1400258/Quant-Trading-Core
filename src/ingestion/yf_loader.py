import yfinance as yf
import pandas as pd
from typing import List, Any
from .data_loader import BaseDataLoader
from loguru import logger
from src.common.data_utils import validate_ohlcv, normalize_column_names

class YFinanceLoader(BaseDataLoader):
    """
    Data loader implementation using yfinance API.
    """
    
    def fetch_data(self, symbols: List[str], start_date: str, end_date: str, interval: str = "1d") -> Any:
        logger.info(f"Fetching data for {symbols} from {start_date} to {end_date} (interval: {interval})")
        data = yf.download(symbols, start=start_date, end=end_date, interval=interval, group_by='ticker')
        return data

    def clean_data(self, raw_data: Any) -> pd.DataFrame:
        logger.info("Cleaning and normalizing data")
        if isinstance(raw_data.columns, pd.MultiIndex):
            # yfinance returns (Ticker, Column) MultiIndex when multiple symbols are requested
            df = raw_data.stack(level=0).reset_index()
            df.columns.name = None
            
            # Map symbol column
            possible_symbol_cols = [c for c in df.columns if c not in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            if 'level_1' in df.columns:
                df = df.rename(columns={'level_1': 'Symbol'})
            elif possible_symbol_cols:
                df = df.rename(columns={possible_symbol_cols[0]: 'Symbol'})
        else:
            df = raw_data.reset_index()
            if 'Symbol' not in df.columns:
                df['Symbol'] = "TICKER" 
        
        # Standardize to UTC timestamps
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col]).dt.tz_localize('UTC') if df[date_col].dt.tz is None else df[date_col].dt.tz_convert('UTC')

        if not validate_ohlcv(df):
            logger.warning("Data validation failed for some records")
            
        return df

    def store_data(self, df: pd.DataFrame, filename: str, format: str = "parquet"):
        path = self.processed_data_dir / filename
        logger.info(f"Storing data to {path}")
        if format == "parquet":
            df.to_parquet(path, compression='snappy')
        elif format == "csv":
            df.to_csv(path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
